from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.http import Http404
from django.views.decorators.http import require_http_methods
from .links import phone_digits, play_store_url
from .models import Enquiry
from .notifications import customer_mailto_url, customer_prefill_text, customer_whatsapp_url, deliver, reference

BUSINESSES = [
 {"number":"01","slug":"construction-engineering","name":"Construction & Engineering","category":"Construction, engineering and project management","capabilities":["Construction","Engineering","Project management"]},
 {"number":"02","slug":"real-estate","name":"Real Estate & Property","category":"Real estate and property services","capabilities":["Real estate services","Property services"]},
 {"number":"03","slug":"technology-it-solutions","name":"Technology & IT Solutions","category":"Technology and IT solutions","capabilities":["Technology solutions","IT solutions"]},
 {"number":"04","slug":"automobile","name":"Automobile Services","category":"Automobile services","capabilities":["Automobile services"]},
 {"number":"05","slug":"logistics","name":"Logistics & Supply Chain","category":"Logistics and supply chain","capabilities":["Logistics","Transportation","Import and export"]},
 {"number":"06","slug":"manufacturing","name":"Manufacturing & Industrial","category":"Manufacturing and industrial operations","capabilities":["Manufacturing","Industrial operations"]},
 {"number":"07","slug":"healthcare","name":"Healthcare Services","category":"Healthcare support services","capabilities":["Healthcare support","Pharmaceutical distribution","Medical supply services"]},
 {"number":"08","slug":"retail-agriculture","name":"Retail & Agriculture","category":"Retail trading and agribusiness","capabilities":["Retail trading","Agriculture","Agribusiness"]},
 {"number":"09","slug":"consultancy","name":"Consultancy Services","category":"Consultancy services","capabilities":["Consultancy"]},
 {"number":"10","slug":"investments","name":"Investments & Venture Development","category":"Investment and venture development","capabilities":["Investment","Venture development"]},
]
BUSINESS_ENQUIRY_TYPES = {
    "construction-engineering": "construction", "real-estate": "real_estate",
    "technology-it-solutions": "technology", "automobile": "automobile", "logistics": "logistics",
    "manufacturing": "manufacturing", "healthcare": "healthcare", "retail-agriculture": "retail_agriculture",
    "consultancy": "consultancy", "investments": "investment",
}
CHANNELS = ("whatsapp", "email")
COMPANY = {"name":"NUVAIX GROUP","legal_name":"NUVAIX SOLUTIONS LTD","rc":"9597904","tagline":"INNOVATE • BUILD • DELIVER • GROW"}
def common(**kwargs):
    return {"company": COMPANY, "businesses": BUSINESSES, **kwargs}

def home(request):
    return render(request, "core/home.html", common(title="A diversified group. A shared ambition.", active="home"))

def businesses(request):
    return render(request, "core/businesses.html", common(title="Our business ecosystem", active="businesses"))

def business_detail(request, slug):
    business = next((item for item in BUSINESSES if item["slug"] == slug), None)
    if business is None:
        raise Http404("Business division not found")
    return render(request, "core/business_detail.html", common(title=business["name"], business=business, active="businesses", enquiry_type=BUSINESS_ENQUIRY_TYPES.get(slug, "general"), app_url=play_store_url(slug)))

def about(request):
    return render(request, "core/about.html", common(title="Built on purpose. Focused on progress.", active="about"))

def technology(request):
    return render(request, "core/technology.html", common(title="Technology that moves business forward.", active="technology", app_url=play_store_url("technology")))

def paint(request):
    return render(request, "core/paint.html", common(title="Colour your world with confidence.", active="paint", app_url=play_store_url("paint")))

def projects(request):
    return render(request, "core/empty_section.html", common(title="Projects", active="projects", eyebrow="Our work", description="Project stories will be published here as approved project information becomes available.", section="projects"))

def insights(request):
    return render(request, "core/empty_section.html", common(title="Insights", active="insights", eyebrow="Ideas and perspectives", description="Articles and company updates will appear here when approved for publication.", section="insights"))

def careers(request):
    return render(request, "core/empty_section.html", common(title="Build what comes next.", active="careers", eyebrow="Careers", description="There are no verified open positions published at this time. Contact us to make a general enquiry.", section="careers"))

def partnerships(request):
    return render(request, "core/empty_section.html", common(title="Let's build meaningful partnerships.", active="partnerships", eyebrow="Partnerships", description="We welcome thoughtful enquiries from organizations aligned with our areas of work.", section="partnerships"))

def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return (forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")) or "unknown"


def _rate_limited(request):
    """Allow at most ENQUIRY_RATE_LIMIT submissions per IP per hour."""
    key = f"enquiry-rate:{_client_ip(request)}"
    cache.add(key, 0, 3600)
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, 3600)
        count = 1
    return count > settings.ENQUIRY_RATE_LIMIT


def _contact_page(request, form_data, channels, status=200):
    return render(request, "core/contact.html", common(
        title="Start a conversation", active="contact", form_data=form_data,
        selected_channels=channels, enquiry_choices=Enquiry.ENQUIRY_TYPES), status=status)


@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "GET":
        channels = [c for c in request.GET.getlist("via") if c in CHANNELS] or ["whatsapp"]
        return _contact_page(request, {}, channels)

    data = request.POST
    if data.get("website"):  # honeypot field: real visitors never see or fill it
        return redirect("contact")
    channels = [c for c in CHANNELS if c in data.getlist("channels")]
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    enquiry_type = data.get("enquiry_type", "general")
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()
    errors = []
    if not name or len(name) > 120: errors.append("Please enter your name.")
    try: validate_email(email)
    except ValidationError: errors.append("Please enter a valid email address.")
    if enquiry_type not in dict(Enquiry.ENQUIRY_TYPES): errors.append("Please choose a valid enquiry type.")
    if not subject or len(subject) > 180: errors.append("Please enter a subject.")
    if not message or len(message) > 5000: errors.append("Please enter a message (up to 5,000 characters).")
    if not channels: errors.append("Please choose how to send your enquiry: WhatsApp, email, or both.")
    if "whatsapp" in channels and not phone_digits(phone):
        errors.append("Please enter your phone number so our team can reply on WhatsApp.")
    if not errors and _rate_limited(request):
        errors.append("You have sent several enquiries recently. Please try again later or chat with us on WhatsApp.")
    if errors:
        for error in errors: messages.error(request, error)
        return _contact_page(request, data, channels or ["whatsapp"])

    enquiry = Enquiry.objects.create(
        name=name, email=email, phone=phone[:40], enquiry_type=enquiry_type,
        subject=subject, message=message, channels=",".join(channels))
    deliver(enquiry)
    request.session["enquiry_result"] = {
        "ref": reference(enquiry),
        "whatsapp": enquiry.whatsapp_status,
        "email": enquiry.email_status,
        # Fallback links are offered whenever automatic delivery did not happen.
        "wa_url": customer_whatsapp_url(enquiry) if enquiry.whatsapp_status in ("manual", "failed") else "",
        "group_url": settings.WHATSAPP_GROUP_INVITE_URL if settings.WHATSAPP_GROUP_PUBLIC and enquiry.whatsapp_status in ("manual", "failed") else "",
        "group_text": customer_prefill_text(enquiry) if settings.WHATSAPP_GROUP_PUBLIC and enquiry.whatsapp_status in ("manual", "failed") else "",
        "mailto_url": customer_mailto_url(enquiry) if enquiry.email_status in ("skipped", "failed") and "email" in channels else "",
    }
    return redirect("contact_sent")


def contact_sent(request):
    result = request.session.get("enquiry_result")
    if not result:
        return redirect("contact")
    return render(request, "core/contact_sent.html", common(title="Thank you", active="contact", result=result))


def legal(request, kind):
    title = "Privacy notice" if kind == "privacy" else "Terms of use"
    description = ("This site collects the information you submit through the contact form to respond to your enquiry. Depending on the option you choose, your enquiry is forwarded to the NUVAIX team through a private WhatsApp group and/or by email. Contact the company for questions about data handling. This starter notice should be reviewed by qualified counsel before launch." if kind == "privacy" else "Use this website lawfully and do not attempt to disrupt, misuse, or gain unauthorized access to its systems. These terms require legal review before production launch.")
    return render(request, "core/legal.html", common(title=title, active=kind, description=description))
