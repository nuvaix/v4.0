import json
import urllib.error
from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .links import phone_digits, play_store_url
from .models import Enquiry

PLAY = "https://play.google.com/store/apps/details?id=com.nuvaix.app"
VALID = {
    "name": "Ada Example", "email": "ada@example.com", "phone": "+2348031234567",
    "enquiry_type": "general", "subject": "Test enquiry", "message": "A genuine question.",
    "channels": ["whatsapp"],
}


def post(client, **overrides):
    return client.post(reverse("contact"), {**VALID, **overrides})


class CorporateSiteTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_main_pages_load(self):
        for route in ["home", "about", "businesses", "technology", "paint", "projects", "insights", "careers", "partnerships", "contact"]:
            with self.subTest(route=route):
                self.assertEqual(self.client.get(reverse(route)).status_code, 200)

    def test_business_detail(self):
        response = self.client.get(reverse("business_detail", args=["technology-it-solutions"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Technology &amp; IT Solutions")

    def test_business_detail_preselects_enquiry_type(self):
        response = self.client.get(reverse("business_detail", args=["real-estate"]))
        self.assertContains(response, "?type=real_estate")

    def test_sent_page_without_submission_redirects(self):
        self.assertRedirects(self.client.get(reverse("contact_sent")), reverse("contact"))


class EnquiryFormTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_whatsapp_without_gateway_offers_manual_link(self):
        response = post(self.client)
        self.assertRedirects(response, reverse("contact_sent"))
        enquiry = Enquiry.objects.get()
        self.assertEqual((enquiry.channels, enquiry.whatsapp_status, enquiry.email_status), ("whatsapp", "manual", "skipped"))
        page = self.client.get(reverse("contact_sent"))
        self.assertContains(page, "Open WhatsApp")
        self.assertContains(page, "wa.me/2349132165565")

    @override_settings(WHATSAPP_GROUP_PUBLIC=True, WHATSAPP_GROUP_INVITE_URL="https://chat.whatsapp.com/ABC123")
    def test_group_link_mode(self):
        post(self.client)
        page = self.client.get(reverse("contact_sent"))
        self.assertContains(page, "https://chat.whatsapp.com/ABC123")
        self.assertContains(page, "Copy my message")
        self.assertContains(page, "A genuine question.")

    def test_group_link_hidden_by_default(self):
        post(self.client)
        self.assertNotContains(self.client.get(reverse("contact_sent")), "chat.whatsapp.com")

    @override_settings(WHATSAPP_GATEWAY_TOKEN="token", WHATSAPP_GROUP_ID="120363000000000000@g.us")
    @patch("core.notifications.urllib.request.urlopen")
    def test_whatsapp_posts_into_group_via_gateway(self, urlopen):
        urlopen.return_value.__enter__.return_value.status = 200
        post(self.client)
        self.assertEqual(Enquiry.objects.get().whatsapp_status, "sent")
        request = urlopen.call_args[0][0]
        body = json.loads(request.data)
        self.assertEqual(body["to"], "120363000000000000@g.us")
        self.assertIn("Ada Example", body["body"])
        self.assertIn("https://wa.me/2348031234567", body["body"])  # one-tap reply link for staff
        self.assertEqual(request.get_header("Authorization"), "Bearer token")
        self.assertNotContains(self.client.get(reverse("contact_sent")), "Open WhatsApp")

    @override_settings(WHATSAPP_GATEWAY_TOKEN="token", WHATSAPP_GROUP_ID="120363000000000000@g.us")
    @patch("core.notifications.urllib.request.urlopen", side_effect=urllib.error.URLError("boom"))
    def test_gateway_failure_falls_back_to_manual_link(self, _urlopen):
        post(self.client)
        self.assertEqual(Enquiry.objects.get().whatsapp_status, "failed")
        self.assertContains(self.client.get(reverse("contact_sent")), "Open WhatsApp")

    @override_settings(EMAIL_CONFIGURED=True, NUVAIX_EMAIL="team@example.com", DEFAULT_FROM_EMAIL="site@example.com")
    def test_email_channel_sends_to_team_with_reply_to(self):
        post(self.client, channels=["email"], phone="")
        enquiry = Enquiry.objects.get()
        self.assertEqual((enquiry.whatsapp_status, enquiry.email_status), ("skipped", "sent"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["team@example.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["ada@example.com"])
        self.assertIn("A genuine question.", mail.outbox[0].body)

    @override_settings(EMAIL_CONFIGURED=False, NUVAIX_EMAIL="team@example.com")
    def test_email_not_configured_offers_mailto(self):
        post(self.client, channels=["email"], phone="")
        self.assertEqual(Enquiry.objects.get().email_status, "skipped")
        self.assertContains(self.client.get(reverse("contact_sent")), "mailto:team@example.com")

    @override_settings(EMAIL_CONFIGURED=True, NUVAIX_EMAIL="team@example.com")
    def test_both_channels(self):
        post(self.client, channels=["whatsapp", "email"])
        enquiry = Enquiry.objects.get()
        self.assertEqual(enquiry.channels, "whatsapp,email")
        self.assertEqual((enquiry.whatsapp_status, enquiry.email_status), ("manual", "sent"))

    def test_requires_a_channel(self):
        response = post(self.client, channels=[])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_whatsapp_requires_phone(self):
        response = post(self.client, phone="")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_rejects_invalid_email(self):
        response = post(self.client, email="not-an-email")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_honeypot_blocks_bots(self):
        post(self.client, website="http://spam.example")
        self.assertEqual(Enquiry.objects.count(), 0)

    @override_settings(ENQUIRY_RATE_LIMIT=1)
    def test_rate_limit(self):
        post(self.client)
        response = post(self.client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Enquiry.objects.count(), 1)


class AndroidInstallButtonTests(TestCase):
    @override_settings(PLAY_STORE_URL="", PLAY_STORE_URLS={})
    def test_coming_soon_when_no_link(self):
        for url in [reverse("paint"), reverse("technology"), reverse("business_detail", args=["healthcare"])]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "Coming soon")
                self.assertNotContains(response, "play.google.com")

    @override_settings(PLAY_STORE_URL=PLAY, PLAY_STORE_URLS={})
    def test_install_button_links_to_play_store(self):
        for url in [reverse("paint"), reverse("technology"), reverse("business_detail", args=["real-estate"]), reverse("business_detail", args=["healthcare"])]:
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), "play.google.com/store/apps/details?id=com.nuvaix.app")

    @override_settings(PLAY_STORE_URL=PLAY, PLAY_STORE_URLS={"REAL_ESTATE": "https://play.google.com/store/apps/details?id=com.nuvaix.realestate"})
    def test_per_division_override(self):
        self.assertContains(self.client.get(reverse("business_detail", args=["real-estate"])), "com.nuvaix.realestate")
        self.assertContains(self.client.get(reverse("paint")), "com.nuvaix.app")

    @override_settings(PLAY_STORE_URL=PLAY, PLAY_STORE_URLS={})
    def test_play_url_is_tagged_for_analytics(self):
        self.assertIn("referrer=utm_source%3Dnuvaix_website", play_store_url("paint"))


class HelperTests(TestCase):
    def test_phone_digits(self):
        self.assertEqual(phone_digits("0803 123 4567"), "2348031234567")
        self.assertEqual(phone_digits("+234 803 123 4567"), "2348031234567")
        self.assertEqual(phone_digits("00234-803-123-4567"), "2348031234567")
        self.assertEqual(phone_digits("abc"), "")
