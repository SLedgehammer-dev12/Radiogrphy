# -*- coding: utf-8 -*-
"""
ASME B31.3 — Process Piping, Table 341.3.2 acceptance criteria.

Starter evaluator for Normal Fluid Service and Severe Cyclic Conditions.
Limits below are engineering approximations of Table 341.3.2; verify against
the current edition of ASME B31.3 before formal use.
"""


class ASMEB31_3Evaluator:
    SERVICES = ("normal", "severe")

    def _msg(self, lang, key, *args):
        table = {
            "reject": ("{} {} hizmetinde kabul edilmez.", "{} is not permitted for {} service."),
            "por_size": ("Gözenek çapı ({:.1f} mm) {} hizmeti limitini ({:.1f} mm) aşıyor.",
                         "Pore size ({:.1f} mm) exceeds the {} service limit ({:.1f} mm)."),
            "por_accum": ("Gözenek yığılma uzunluğu ({:.1f} mm) {} hizmeti limitini ({:.1f} mm) aşıyor.",
                          "Porosity accumulated length ({:.1f} mm) exceeds the {} service limit ({:.1f} mm)."),
            "slag_w": ("Cüruf genişliği ({:.1f} mm) {} hizmeti limitini ({:.1f} mm) aşıyor.",
                       "Slag width ({:.1f} mm) exceeds the {} service limit ({:.1f} mm)."),
            "undercut_d": ("Yanma oluğu derinliği ({:.2f} mm) {} hizmeti limitini ({:.2f} mm) aşıyor.",
                           "Undercut depth ({:.2f} mm) exceeds the {} service limit ({:.2f} mm)."),
            "accept": ("Kusur ebatları ASME B31.3 Tablo 341.3.2 ({} hizmeti) limitleri dahilindedir. KABUL EDİLEBİLİR.",
                       "Defect dimensions are within ASME B31.3 Table 341.3.2 ({} service) limits. ACCEPTABLE."),
        }
        text = table.get(key, ("", ""))[0 if lang == "tr" else 1]
        return text.format(*args) if args else text

    def _svc(self, service, lang):
        if lang == "tr":
            return "Severe Cyclic" if service == "severe" else "Normal Fluid"
        return "Severe Cyclic" if service == "severe" else "Normal Fluid"

    def evaluate(self, defect_type, t, length, width, accumulated, service="normal", lang="tr"):
        is_accepted = True
        reasons = []
        service = (service or "normal").lower()
        if service not in self.SERVICES:
            service = "normal"
        svc = self._svc(service, lang)

        if defect_type == "defect_crack":
            return False, self._msg(lang, "reject", "Çatlaklar (Cracks)", svc)
        if defect_type in ("defect_if", "defect_ic"):
            return False, self._msg(lang, "reject", "Yetersiz ergime (IF)", svc)
        if defect_type == "defect_ip":
            return False, self._msg(lang, "reject", "Yetersiz nüfuziyet (IP)", svc)
        if defect_type == "defect_burn_through":
            return False, self._msg(lang, "reject", "Kök yanması (Burn-through)", svc)

        if defect_type == "defect_porosity":
            max_pore = 3.0 if service == "normal" else 1.6
            max_accum = 0.03 * 300.0 if service == "normal" else 0.015 * 300.0
            max_dim = max(length, width)
            if max_dim > max_pore:
                is_accepted = False
                reasons.append(self._msg(lang, "por_size", max_dim, svc, max_pore))
            if accumulated > max_accum:
                is_accepted = False
                reasons.append(self._msg(lang, "por_accum", accumulated, svc, max_accum))

        elif defect_type == "defect_slag":
            max_w = 1.6 if service == "normal" else 0.8
            if width > max_w:
                is_accepted = False
                reasons.append(self._msg(lang, "slag_w", width, svc, max_w))

        elif defect_type == "defect_undercut":
            max_d = 0.8 if service == "normal" else 0.4
            if width > max_d:
                is_accepted = False
                reasons.append(self._msg(lang, "undercut_d", width, svc, max_d))

        if is_accepted:
            return True, self._msg(lang, "accept", svc)
        return False, " | ".join(reasons)