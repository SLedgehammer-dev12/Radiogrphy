# -*- coding: utf-8 -*-
"""
ISO 5817 — Quality levels for imperfections in fusion-welded joints.

Starter evaluator covering the main imperfection categories at quality levels
B (high), C (medium) and D (low). The limits below are engineering
approximations of ISO 5817:2014/2023 acceptance tables (expressed relative to
the nominal thickness s); they must be verified against the current edition of
the standard before use in formal acceptance decisions.
"""


class ISO5817Evaluator:
    LEVELS = ("B", "C", "D")

    def _msg(self, lang, key, *args):
        table = {
            "crack": ("Çatlaklar ISO 5817'de tüm kalite seviyelerinde (B/C/D) kabul edilmez.",
                      "Cracks are not permitted at any ISO 5817 quality level (B/C/D)."),
            "ip_len": ("Yetersiz nüfuziyet uzunluğu ({:.1f} mm) {} seviyesi limitini ({:.1f} mm) aşıyor.",
                       "Incomplete penetration length ({:.1f} mm) exceeds the {} level limit ({:.1f} mm)."),
            "ip_accum": ("Yetersiz nüfuziyet 300 mm'deki toplam yığılma ({:.1f} mm) {} seviyesi limitini ({:.1f} mm) aşıyor.",
                         "Incomplete penetration accumulation in 300 mm ({:.1f} mm) exceeds the {} level limit ({:.1f} mm)."),
            "if": ("Yetersiz ergime {} seviyesinde kabul edilmez.",
                   "Incomplete fusion is not permitted at level {}."),
            "por_size": ("Gözenek çapı ({:.1f} mm) {} seviyesi limitini ({:.1f} mm) aşıyor.",
                         "Pore size ({:.1f} mm) exceeds the {} level limit ({:.1f} mm)."),
            "por_accum": ("Gözenek 300 mm'deki toplam yığılma ({:.1f} mm) {} seviyesi limitini ({:.1f} mm) aşıyor.",
                          "Porosity accumulation in 300 mm ({:.1f} mm) exceeds the {} level limit ({:.1f} mm)."),
            "slag_w": ("Cüruf genişliği ({:.1f} mm) {} seviyesi limitini ({:.1f} mm) aşıyor.",
                       "Slag width ({:.1f} mm) exceeds the {} level limit ({:.1f} mm)."),
            "undercut_d": ("Yanma oluğu derinliği ({:.2f} mm) {} seviyesi limitini ({:.2f} mm) aşıyor.",
                           "Undercut depth ({:.2f} mm) exceeds the {} level limit ({:.2f} mm)."),
            "burn": ("Kök yanması (burn-through) {} seviyesinde kabul edilmez.",
                     "Burn-through is not permitted at level {}."),
            "accept": ("Kusur ebatları ISO 5817 {} seviyesi limitleri dahilindedir. KABUL EDİLEBİLİR.",
                       "Defect dimensions are within the ISO 5817 level {} limits. ACCEPTABLE."),
        }
        text = table.get(key, ("", ""))[0 if lang == "tr" else 1]
        return text.format(*args) if args else text

    def _porosity_limits(self, level, t):
        return {
            "max_size": min(3.0, 0.3 * t) if level == "B" else
                        min(4.0, 0.4 * t) if level == "C" else
                        min(5.0, 0.5 * t),
            "accum_300": 9.0 if level == "B" else 18.0 if level == "C" else 27.0,
        }

    def _ip_limits(self, level, t):
        if level == "B":
            return {"len": 0.0, "accum": 0.0}   # not permitted
        if level == "C":
            return {"len": min(3.0, 0.4 * t), "accum": 6.0}
        return {"len": min(5.0, 0.5 * t), "accum": 9.0}

    def evaluate(self, defect_type, t, length, width, accumulated, level="C", lang="tr"):
        """
        Evaluates a weld defect per ISO 5817 quality level.
        Returns (is_accepted, reason_str).
        """
        is_accepted = True
        reasons = []
        level = (level or "C").upper()
        if level not in self.LEVELS:
            level = "C"

        if defect_type == "defect_crack":
            return False, self._msg(lang, "crack")

        if defect_type == "defect_ip":
            lim = self._ip_limits(level, t)
            if level == "B":
                return False, self._msg(lang, "ip_len", length, "B", lim["len"])
            if length > lim["len"]:
                is_accepted = False
                reasons.append(self._msg(lang, "ip_len", length, level, lim["len"]))
            if accumulated > lim["accum"]:
                is_accepted = False
                reasons.append(self._msg(lang, "ip_accum", accumulated, level, lim["accum"]))

        elif defect_type in ("defect_if", "defect_ic"):
            # Incomplete fusion / root penetration: generally not permitted at B; at C/D limited.
            if level in ("B", "C"):
                return False, self._msg(lang, "if", level)
            lim = {"len": min(4.0, 0.4 * t), "accum": 8.0}
            if length > lim["len"]:
                is_accepted = False
                reasons.append(self._msg(lang, "ip_len", length, level, lim["len"]))
            if accumulated > lim["accum"]:
                is_accepted = False
                reasons.append(self._msg(lang, "ip_accum", accumulated, level, lim["accum"]))

        elif defect_type == "defect_porosity":
            lim = self._porosity_limits(level, t)
            max_dim = max(length, width)
            if max_dim > lim["max_size"]:
                is_accepted = False
                reasons.append(self._msg(lang, "por_size", max_dim, level, lim["max_size"]))
            if accumulated > lim["accum_300"]:
                is_accepted = False
                reasons.append(self._msg(lang, "por_accum", accumulated, level, lim["accum_300"]))

        elif defect_type == "defect_slag":
            max_w = min(1.5, 0.3 * t) if level == "B" else \
                    min(2.5, 0.4 * t) if level == "C" else \
                    min(3.5, 0.5 * t)
            if width > max_w:
                is_accepted = False
                reasons.append(self._msg(lang, "slag_w", width, level, max_w))

        elif defect_type == "defect_undercut":
            max_d = 0.5 if level == "B" else 1.0 if level == "C" else 1.5
            if width > max_d:
                is_accepted = False
                reasons.append(self._msg(lang, "undercut_d", width, level, max_d))

        elif defect_type == "defect_burn_through":
            if level in ("B", "C"):
                return False, self._msg(lang, "burn", level)
            if width > 2.0:
                is_accepted = False
                reasons.append(self._msg(lang, "undercut_d", width, level, 2.0))

        if is_accepted:
            return True, self._msg(lang, "accept", level)
        return False, " | ".join(reasons)