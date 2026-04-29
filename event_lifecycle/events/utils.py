import io
import qrcode
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas as rl_canvas


def generate_qr(data: str) -> bytes:
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def generate_qr_base64(data: str) -> str:
    import base64
    return base64.b64encode(generate_qr(data)).decode()


def generate_pdf(participant) -> HttpResponse:
    buffer = io.BytesIO()
    width, height = landscape(A4)
    c = rl_canvas.Canvas(buffer, pagesize=landscape(A4))

    # Background gradient effect
    c.setFillColor(colors.HexColor('#f0f4ff'))
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Decorative top bar
    c.setFillColor(colors.HexColor('#1a3c8f'))
    c.rect(0, height - 2*cm, width, 2*cm, fill=True, stroke=False)

    # Decorative bottom bar
    c.setFillColor(colors.HexColor('#1a3c8f'))
    c.rect(0, 0, width, 1.5*cm, fill=True, stroke=False)

    # Border
    c.setStrokeColor(colors.HexColor('#1a3c8f'))
    c.setLineWidth(4)
    c.rect(1.2*cm, 1.8*cm, width - 2.4*cm, height - 4*cm, fill=False, stroke=True)

    # Organizer name in top bar
    c.setFont('Helvetica-Bold', 14)
    c.setFillColor(colors.white)
    c.drawCentredString(width / 2, height - 1.3*cm, participant.event.organizer.upper())

    # Certificate title
    c.setFont('Helvetica-Bold', 38)
    c.setFillColor(colors.HexColor('#1a3c8f'))
    c.drawCentredString(width / 2, height - 4.5*cm, 'Certificate of Participation')

    # Divider line
    c.setStrokeColor(colors.HexColor('#c9a84c'))
    c.setLineWidth(2)
    c.line(width*0.2, height - 5.2*cm, width*0.8, height - 5.2*cm)

    c.setFont('Helvetica', 16)
    c.setFillColor(colors.HexColor('#555555'))
    c.drawCentredString(width / 2, height - 6.2*cm, 'This is to certify that')

    # Name
    c.setFont('Helvetica-Bold', 30)
    c.setFillColor(colors.HexColor('#1a3c8f'))
    c.drawCentredString(width / 2, height - 8*cm, participant.name)

    # Underline name
    name_width = c.stringWidth(participant.name, 'Helvetica-Bold', 30)
    c.setStrokeColor(colors.HexColor('#c9a84c'))
    c.setLineWidth(1.5)
    c.line(width/2 - name_width/2, height - 8.4*cm, width/2 + name_width/2, height - 8.4*cm)

    c.setFont('Helvetica', 16)
    c.setFillColor(colors.HexColor('#555555'))
    c.drawCentredString(width / 2, height - 9.4*cm, 'has successfully participated in')

    c.setFont('Helvetica-Bold', 22)
    c.setFillColor(colors.HexColor('#1a3c8f'))
    c.drawCentredString(width / 2, height - 10.8*cm, participant.event.name)

    c.setFont('Helvetica', 13)
    c.setFillColor(colors.HexColor('#666666'))
    c.drawCentredString(width / 2, height - 11.8*cm,
                        f'held on {participant.event.date.strftime("%B %d, %Y")} at {participant.event.venue}')

    # Bottom info
    c.setFont('Helvetica', 10)
    c.setFillColor(colors.white)
    c.drawString(1.8*cm, 0.5*cm,
                 f'Student ID: {participant.student_id}   |   Ref: {participant.transaction_id}')
    c.drawRightString(width - 1.8*cm, 0.5*cm, f'Token: {participant.token}')

    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="certificate_{participant.student_id}.pdf"'
    )
    return response


def send_registration_email(participant, request):
    """Send registration confirmation email with QR code."""
    try:
        event_url = request.build_absolute_uri(f'/event/{participant.event.pk}/')
        feedback_url = request.build_absolute_uri(f'/feedback/{participant.token}/')
        cert_url = request.build_absolute_uri(f'/certificate/{participant.token}/')

        subject = f"Registration Confirmed – {participant.event.name}"
        context = {
            'participant': participant,
            'event_url': event_url,
            'feedback_url': feedback_url,
            'cert_url': cert_url,
        }
        html_content = render_to_string('events/email_registration.html', context)
        text_content = (
            f"Hi {participant.name},\n\n"
            f"You are registered for {participant.event.name}!\n"
            f"Date: {participant.event.date}\n"
            f"Venue: {participant.event.venue}\n\n"
            f"Event page: {event_url}\n"
        )

        msg = EmailMultiAlternatives(subject, text_content,
                                     settings.DEFAULT_FROM_EMAIL, [participant.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        participant.confirmation_sent = True
        participant.save(update_fields=['confirmation_sent'])
    except Exception:
        pass  # Don't break registration if email fails


def send_certificate_email(participant, request):
    """Send certificate PDF via email."""
    try:
        subject = f"Your Certificate – {participant.event.name}"
        text_content = (
            f"Hi {participant.name},\n\n"
            f"Congratulations! Your certificate for {participant.event.name} is attached.\n"
        )
        msg = EmailMultiAlternatives(subject, text_content,
                                     settings.DEFAULT_FROM_EMAIL, [participant.email])

        # Generate PDF and attach
        pdf_buf = io.BytesIO()
        _write_pdf(participant, pdf_buf)
        pdf_buf.seek(0)
        msg.attach(f'certificate_{participant.student_id}.pdf', pdf_buf.read(), 'application/pdf')
        msg.send()

        participant.certificate_sent = True
        participant.save(update_fields=['certificate_sent'])
    except Exception:
        pass


def _write_pdf(participant, buffer):
    """Write PDF to a buffer (reused by email attachment)."""
    width, height = landscape(A4)
    c = rl_canvas.Canvas(buffer, pagesize=landscape(A4))
    c.setFillColor(colors.HexColor('#f0f4ff'))
    c.rect(0, 0, width, height, fill=True, stroke=False)
    c.setFillColor(colors.HexColor('#1a3c8f'))
    c.rect(0, height - 2*cm, width, 2*cm, fill=True, stroke=False)
    c.setFont('Helvetica-Bold', 38)
    c.setFillColor(colors.HexColor('#1a3c8f'))
    c.drawCentredString(width / 2, height - 4.5*cm, 'Certificate of Participation')
    c.setFont('Helvetica-Bold', 30)
    c.drawCentredString(width / 2, height - 8*cm, participant.name)
    c.setFont('Helvetica', 16)
    c.setFillColor(colors.HexColor('#555555'))
    c.drawCentredString(width / 2, height - 10.8*cm, participant.event.name)
    c.save()
