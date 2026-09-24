import os
import json
import io
import boto3

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError


# ============================================================
# AWS CLIENTS
# ============================================================

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://host.docker.internal:4566"),
    region_name="us-east-1",
)

sns = boto3.client(
    "sns",
    endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://host.docker.internal:4566"),
    region_name="us-east-1",
)


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_BUCKET = os.environ.get(
    "OUTPUT_BUCKET",
    "image-output"
)

SNS_TOPIC_ARN = os.environ.get(
    "SNS_TOPIC_ARN",
    ""
)

IMAGE_SIZES = {
    "small": (300, 300),
    "medium": (600, 600),
    "large": (1200, 1200)
}

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tiff"
}


# ============================================================
# WATERMARK
# ============================================================

def add_watermark(image, text):

    image = image.copy()

    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(
            "DejaVuSans.ttf",
            max(20, image.width // 30)
        )
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = image.width - text_width - 30
    y = image.height - text_height - 30

    draw.rectangle(
        (
            x - 10,
            y - 5,
            x + text_width + 10,
            y + text_height + 5
        ),
        fill="black"
    )

    draw.text(
        (x, y),
        text,
        fill="white",
        font=font
    )

    return image


# ============================================================
# RESIZE
# ============================================================

def resize_image(image, size):

    output = image.copy()

    output.thumbnail(
        size,
        Image.Resampling.LANCZOS
    )

    return output


# ============================================================
# JPEG TO BYTES
# ============================================================

def image_to_jpeg_bytes(image):

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=70,
        optimize=True
    )

    buffer.seek(0)

    return buffer


# ============================================================
# PDF TO BYTES
# ============================================================

def image_to_pdf_bytes(image):

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PDF",
        resolution=100.0
    )

    buffer.seek(0)

    return buffer


# ============================================================
# SNS NOTIFICATION
# ============================================================

def send_notification(subject, message):

    if not SNS_TOPIC_ARN:
        print("SNS topic ARN not configured.")

        return

    try:

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )

        print("SNS notification sent.")

    except Exception as error:

        print(
            f"SNS notification failed: {error}"
        )


# ============================================================
# LAMBDA HANDLER
# ============================================================

def lambda_handler(event, context):

    print("=" * 70)
    print("              IMAGE PROCESSING LAMBDA")
    print("=" * 70)

    print(
        "Received event:"
    )

    print(
        json.dumps(
            event,
            indent=2
        )
    )

    try:

        # ----------------------------------------------------
        # READ S3 EVENT
        # ----------------------------------------------------

        record = event["Records"][0]

        input_bucket = record["s3"]["bucket"]["name"]

        input_key = record["s3"]["object"]["key"]

        print("\nInput bucket:")
        print(input_bucket)

        print("\nInput object:")
        print(input_key)

        # ----------------------------------------------------
        # DOWNLOAD ORIGINAL IMAGE
        # ----------------------------------------------------

        response = s3.get_object(
            Bucket=input_bucket,
            Key=input_key
        )

        image_data = response["Body"].read()

        print(
            f"\nDownloaded: "
            f"{len(image_data)} bytes"
        )

        # ----------------------------------------------------
        # OPEN IMAGE
        # ----------------------------------------------------

        try:

            original_image = Image.open(
                io.BytesIO(image_data)
            )

            original_image.verify()

        except UnidentifiedImageError:

            raise ValueError(
                "Uploaded file is not a valid image."
            )

        # Re-open after verify()

        original_image = Image.open(
            io.BytesIO(image_data)
        ).convert("RGB")

        print(
            f"\nOriginal dimensions: "
            f"{original_image.width} x "
            f"{original_image.height}"
        )

        # ----------------------------------------------------
        # READ OPTIONAL SETTINGS FROM EVENT
        # ----------------------------------------------------

        settings = event.get(
            "processing_settings",
            {}
        )

        image_watermark_enabled = settings.get(
            "image_watermark_enabled",
            False
        )

        image_watermark_text = settings.get(
            "image_watermark_text",
            ""
        )

        image_watermark_targets = set(
            settings.get(
                "image_watermark_targets",
                []
            )
        )

        pdf_watermark_enabled = settings.get(
            "pdf_watermark_enabled",
            False
        )

        pdf_watermark_text = settings.get(
            "pdf_watermark_text",
            ""
        )

        # ----------------------------------------------------
        # CREATE OUTPUTS
        # ----------------------------------------------------

        input_name = os.path.basename(
            input_key
        )

        input_stem = os.path.splitext(
            input_name
        )[0]

        generated_files = []

        # ----------------------------------------------------
        # CREATE 3 JPGS
        # ----------------------------------------------------

        for name, size in IMAGE_SIZES.items():

            print(
                f"\nCreating {name} image..."
            )

            processed_image = resize_image(
                original_image,
                size
            )

            watermark_applied = False

            if (
                image_watermark_enabled
                and name in image_watermark_targets
            ):

                processed_image = add_watermark(
                    processed_image,
                    image_watermark_text
                )

                watermark_applied = True

            output_key = (
                f"{input_stem}_{name}.jpg"
            )

            output_buffer = image_to_jpeg_bytes(
                processed_image
            )

            s3.put_object(
                Bucket=OUTPUT_BUCKET,
                Key=output_key,
                Body=output_buffer.getvalue(),
                ContentType="image/jpeg"
            )

            generated_files.append(
                output_key
            )

            print(
                f"Created: {output_key}"
            )

            print(
                f"Dimensions: "
                f"{processed_image.width} x "
                f"{processed_image.height}"
            )

            print(
                f"Watermark: "
                f"{'YES' if watermark_applied else 'NO'}"
            )

        # ----------------------------------------------------
        # CREATE PDF
        # ----------------------------------------------------

        print("\nCreating PDF...")

        pdf_image = original_image.copy()

        pdf_watermark_applied = False

        if pdf_watermark_enabled:

            pdf_image = add_watermark(
                pdf_image,
                pdf_watermark_text
            )

            pdf_watermark_applied = True

        pdf_key = (
            f"{input_stem}.pdf"
        )

        pdf_buffer = image_to_pdf_bytes(
            pdf_image
        )

        s3.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=pdf_key,
            Body=pdf_buffer.getvalue(),
            ContentType="application/pdf"
        )

        generated_files.append(
            pdf_key
        )

        print(
            f"Created: {pdf_key}"
        )

        print(
            "PDF watermark:",
            "YES"
            if pdf_watermark_applied
            else "NO"
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        message = (
            f"Image processing completed successfully.\n\n"
            f"Input: {input_key}\n"
            f"Output bucket: {OUTPUT_BUCKET}\n\n"
            f"Generated files:\n"
        )

        for file in generated_files:

            message += f"- {file}\n"

        send_notification(
            "Image Processing Successful",
            message
        )

        print("\n" + "=" * 70)
        print("STATUS: SUCCESS")
        print("=" * 70)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "input": input_key,
                    "outputs": generated_files
                }
            )
        }

    except Exception as error:

        print("\n" + "=" * 70)
        print("STATUS: FAILED")
        print("=" * 70)

        print(
            f"Error: {error}"
        )

        send_notification(
            "Image Processing Failed",
            (
                f"Image processing failed.\n\n"
                f"Error: {error}"
            )
        )

        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "status": "failed",
                    "error": str(error)
                }
            )
        }