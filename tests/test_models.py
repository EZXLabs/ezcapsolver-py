"""Wire-format mapping for task and solution models."""

from __future__ import annotations

import pytest

from ezcapsolver import (
    AkamaiSBSDSolution,
    AkamaiWebSolution,
    AkamaiWebTask,
    Cloudflare5sSolution,
    Cloudflare5sTask,
    DataDomeSolution,
    DataDomeStep,
    DataDomeTask,
    FunCaptchaClassificationSolution,
    FunCaptchaClassificationTask,
    FunCaptchaTask,
    HCaptchaClassificationSolution,
    HCaptchaClassificationTask,
    HCaptchaSolution,
    HCaptchaTask,
    IncapsulaSolution,
    IncapsulaTask,
    PerimeterXSolution,
    ReCaptchaSolution,
    ReCaptchaV2ClassificationTask,
    ReCaptchaV2EnterpriseTask,
    ReCaptchaV2Task,
    ReCaptchaV3Task,
    ReClassificationSolution,
    SolutionDecodeError,
    TaskMode,
    TaskType,
    TlsForwardTask,
    TlsHttpMethod,
)


def akamai_task(**overrides) -> AkamaiWebTask:
    """Build a fully populated Akamai task, reused by several cases."""
    return AkamaiWebTask(
        page_url="https://example.com",
        v3_url="https://example.com/v3.js",
        ua="UA",
        lang="en",
        abck="abck-value",
        bmsz="bmsz-value",
        script_base64="c2NyaXB0",
        **overrides,
    )


class TestTaskWireMapping:
    def test_camel_case_is_the_default(self):
        assert akamai_task().to_dict()["pageUrl"] == "https://example.com"

    def test_explicit_names_beat_camel_case(self):
        # The uppercase URL in websiteURL and the underscore in script_base64 require explicit
        # wire names; camelCase conversion cannot produce them.
        wire = ReCaptchaV2Task(website_url="https://example.com", website_key="key").to_dict()
        assert "websiteURL" in wire
        assert "websiteUrl" not in wire
        assert "script_base64" in akamai_task().to_dict()

    def test_none_valued_optionals_are_omitted(self):
        wire = ReCaptchaV2Task(website_url="u", website_key="k").to_dict()
        assert set(wire) == {"websiteURL", "websiteKey", "isInvisible"}

    def test_present_optionals_are_kept(self):
        wire = ReCaptchaV2Task(website_url="u", website_key="k", s="s-value").to_dict()
        assert wire["s"] == "s-value"

    def test_v3_defaults_to_invisible(self):
        assert ReCaptchaV3Task(website_url="u", website_key="k").to_dict()["isInvisible"] is True

    def test_extra_fields_are_flattened(self):
        wire = FunCaptchaTask(
            website_url="u", website_key="k", extra={"customField": "v"}
        ).to_dict()
        assert wire["customField"] == "v"

    def test_extra_cannot_overwrite_a_modelled_field(self):
        # An accidental duplicate in pass-through data must not silently replace a modelled field.
        wire = ReCaptchaV2Task(
            website_url="real", website_key="k", extra={"websiteURL": "spoofed"}
        ).to_dict()
        assert wire["websiteURL"] == "real"

    def test_hcaptcha_rqdata_is_lower_case_unlike_cloudflares(self):
        # One letter apart, and getting it wrong raises nothing — the parameter is
        # just ignored. HCaptcha takes a string here and Cloudflare an object, so
        # the two are not interchangeable either.
        hcaptcha = HCaptchaTask(
            website_url="u", website_key="k", lang="en-US", invisible=False, rq_data="rq"
        ).to_dict()
        assert hcaptcha["rqdata"] == "rq"
        assert "rqData" not in hcaptcha

        cloudflare = Cloudflare5sTask(
            website_url="u", proxy="p", rq_data={"cType": "managed"}
        ).to_dict()
        assert cloudflare["rqData"] == {"cType": "managed"}
        assert "rqdata" not in cloudflare

    def test_required_booleans_are_sent_even_when_false(self):
        # For both of these false is a statement rather than an omission: leaving
        # one out lets the service apply its own default instead.
        hcaptcha = HCaptchaTask(
            website_url="u", website_key="k", lang="en-US", invisible=False
        ).to_dict()
        assert hcaptcha["invisible"] is False
        # An unset rqdata has no business appearing in the request.
        assert "rqdata" not in hcaptcha

        forward = TlsForwardTask(tls_type="chrome", proxy="p", url="u").to_dict()
        assert forward["body_raw"] is False

    def test_incapsula_optionals_are_omitted_when_unset(self):
        wire = IncapsulaTask(script="s", script_url="su", page_url="p", ua="UA").to_dict()
        assert "acceptLanguage" not in wire
        assert "pow" not in wire

        supplied = IncapsulaTask(
            script="s", script_url="su", page_url="p", ua="UA", accept_language="en-US", pow="w"
        ).to_dict()
        assert supplied["acceptLanguage"] == "en-US"
        assert supplied["pow"] == "w"

    def test_enums_serialise_as_their_wire_strings(self):
        assert DataDomeTask(html_b64="x", step=DataDomeStep.TWO).to_dict()["step"] == "2"
        task = TlsForwardTask(tls_type="chrome", proxy="p", method=TlsHttpMethod.POST, url="u")
        assert task.to_dict()["method"] == "POST"

    def test_snake_case_survives_when_the_api_uses_it(self):
        assert "tls_type" in TlsForwardTask(tls_type="chrome", proxy="p", url="u").to_dict()

    def test_the_first_akamai_round_needs_no_cookies_or_script(self):
        # Round 0 runs before the site has issued _abck or bm_sz, and the contract
        # marks all three optional with an empty-string default. Requiring them
        # would make callers write "" by hand, and would diverge from the Rust SDK.
        wire = AkamaiWebTask(
            page_url="https://example.com", v3_url="https://example.com/v3.js", ua="UA", lang="en"
        ).to_dict()
        assert wire["abck"] == ""
        assert wire["bmsz"] == ""
        assert wire["script_base64"] == ""
        # index is always sent: the contract wants the field present and non-null,
        # and 0 is the correct value for round 0.
        assert wire["index"] == 0


class TestTaskMetadata:
    def test_a_task_knows_its_own_type_mode_and_solution(self):
        # task_type and solution_type let solve() handle all 23 types without separate
        # branches; mode only records what the service documents.
        task = ReCaptchaV2Task(website_url="u", website_key="k")
        assert task.task_type is TaskType.RECAPTCHA_V2_TASK_PROXYLESS
        assert task.mode is TaskMode.POLLING
        assert ReCaptchaV2ClassificationTask.mode is TaskMode.SYNC
        assert task.solution_type is ReCaptchaSolution

    def test_variants_reuse_the_base_fields_and_only_change_the_type(self):
        base = ReCaptchaV2Task(website_url="u", website_key="k")
        variant = ReCaptchaV2EnterpriseTask(website_url="u", website_key="k")
        assert base.to_dict() == variant.to_dict()
        assert variant.task_type is TaskType.RECAPTCHA_V2_ENTERPRISE_TASK_PROXYLESS

    @pytest.mark.parametrize(
        ("task", "model"),
        [
            (
                FunCaptchaClassificationTask(image="i", question="q"),
                FunCaptchaClassificationSolution,
            ),
            (HCaptchaClassificationTask(), HCaptchaClassificationSolution),
        ],
    )
    def test_unconfirmed_shapes_use_a_placeholder_model(self, task, model):
        # The two types whose shape is unconfirmed each get a placeholder model: a
        # type callers can annotate against, with no invented business fields.
        # Fields get added as each one is confirmed.
        assert task.solution_type is model
        raw = {"objects": [3], "angle": 137.5}
        assert model.from_dict(raw).extra == raw


class TestSolutionDecoding:
    def test_unknown_fields_land_in_extra(self):
        solution = ReCaptchaSolution.from_dict(
            {"gRecaptchaResponse": "token", "brandNewField": {"nested": 1}}
        )
        assert solution.token == "token"
        assert solution.extra == {"brandNewField": {"nested": 1}}

    def test_cloudflare_5s_keeps_every_part_of_the_browser_state(self):
        # The old implementation reduced this structure to a string, losing header and body.
        solution = Cloudflare5sSolution.from_dict(
            {
                "header": {"user-agent": "UA"},
                "cookies": {"cf_clearance": "abc"},
                "tlsVersion": "chrome149",
                "body": "<html/>",
                "sToken": "st",
            }
        )
        assert solution.header == {"user-agent": "UA"}
        assert solution.cookies == {"cf_clearance": "abc"}
        assert solution.body == "<html/>"
        assert solution.tls_version == "chrome149"

    def test_perimeterx_underscored_cookies_map_to_clean_names(self):
        solution = PerimeterXSolution.from_dict(
            {"_px3": "px3", "_pxvid": "vid", "_pxde": "de", "_pxhd": "hd"}
        )
        assert solution.px3 == "px3"
        assert solution.extra == {"_pxhd": "hd"}

    def test_optional_fields_may_be_absent(self):
        assert AkamaiSBSDSolution.from_dict({"payload": "p"}).bm_lso_time is None
        assert AkamaiWebSolution.from_dict({"payload": "p"}).encodedata == ""
        assert HCaptchaSolution.from_dict({"generated_pass_UUID": "u"}).ua is None

    def test_datadome_uses_one_model_for_both_steps(self):
        step1 = DataDomeSolution.from_dict({"url": "https://challenge"})
        step2 = DataDomeSolution.from_dict({"kind": "slider", "url": "https://check", "body": "b"})
        assert step1.url == "https://challenge"
        assert step2.kind == "slider"

    def test_a_missing_required_field_raises_with_the_raw_value(self):
        with pytest.raises(SolutionDecodeError) as excinfo:
            IncapsulaSolution.from_dict({"status": 200})
        # Debugging depends on the raw value, so it must be preserved on the exception.
        assert excinfo.value.raw == {"status": 200}

    def test_a_non_object_solution_raises(self):
        with pytest.raises(SolutionDecodeError):
            ReCaptchaSolution.from_dict("a bare string")


class TestClassificationSolution:
    def test_multi_grid_result(self):
        solution = ReClassificationSolution.from_dict({"type": "multi", "objects": [0, 3, 7]})
        assert solution.type == "multi"
        assert solution.is_multi
        assert not solution.is_single
        assert solution.objects == [0, 3, 7]
        assert solution.has_object is False

    @pytest.mark.parametrize("has_object", [True, False])
    def test_single_image_result(self, has_object):
        solution = ReClassificationSolution.from_dict({"type": "single", "hasObject": has_object})
        assert solution.type == "single"
        assert solution.is_single
        assert not solution.is_multi
        assert solution.has_object is has_object
        assert solution.objects == []

    def test_fields_are_preserved_regardless_of_type(self):
        payload = {
            "type": "single",
            "hasObject": True,
            "objects": [1],
            "confidence": {"score": 0.9},
        }
        solution = ReClassificationSolution.from_dict(payload)
        assert solution.has_object is True
        assert solution.objects == [1]
        assert solution.extra == {"confidence": {"score": 0.9}}
        assert solution.to_dict() == payload

    def test_an_unknown_discriminant_is_kept_verbatim(self):
        # New server-side challenge types must not cause the SDK to fail decoding.
        payload = {"type": "brand-new", "whatever": 1}
        solution = ReClassificationSolution.from_dict(payload)
        assert solution.type == "brand-new"
        assert not solution.is_multi
        assert not solution.is_single
        assert solution.extra == {"whatever": 1}
        assert solution.to_dict() == {**payload, "hasObject": False, "objects": []}

    def test_a_missing_type_does_not_infer_the_result_kind(self):
        solution = ReClassificationSolution.from_dict({"objects": [2]})
        assert solution.type == ""
        assert not solution.is_multi
        assert not solution.is_single
        assert solution.objects == [2]
        assert solution.has_object is False

    def test_extra_cannot_overwrite_the_declared_fields(self):
        solution = ReClassificationSolution(
            type="single",
            has_object=False,
            objects=[],
            extra={"type": "multi", "hasObject": True, "objects": [1], "later": 42},
        )
        assert solution.to_dict() == {
            "type": "single",
            "hasObject": False,
            "objects": [],
            "later": 42,
        }

    def test_a_non_object_solution_carries_the_raw_value_on_error(self):
        with pytest.raises(SolutionDecodeError) as excinfo:
            ReClassificationSolution.from_dict([0, 3])
        assert excinfo.value.raw == [0, 3]
