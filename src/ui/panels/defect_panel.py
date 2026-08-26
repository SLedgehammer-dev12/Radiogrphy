# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QWidget, QGridLayout, QLabel, QComboBox,
                             QLineEdit, QPushButton, QTabWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDoubleValidator


class DefectPanelMixin:
    """Mixin that creates API 1104 defect evaluation tab UI (self.tab_extra)."""

    def _init_defect_panel(self):
        self.tab_extra = QTabWidget()
        self.tab_extra.setObjectName("ExtraTabs")
        tab_defect = QWidget()
        defect_layout = QGridLayout(tab_defect)
        tab_defect.setLayout(defect_layout)
        defect_layout.addWidget(QLabel(self.trans.get("defect_standard")), 0, 0)
        self.cmb_defect_standard = QComboBox()
        self.cmb_defect_standard.addItem(self.trans.get("defect_std_api1104"), "api1104")
        self.cmb_defect_standard.addItem(self.trans.get("defect_std_iso5817"), "iso5817")
        self.cmb_defect_standard.addItem(self.trans.get("defect_std_b31_3"), "b31_3")
        self.cmb_defect_standard.addItem(self.trans.get("defect_std_viii"), "viii")
        self.cmb_defect_standard.currentIndexChanged.connect(self._on_defect_standard_changed)
        defect_layout.addWidget(self.cmb_defect_standard, 0, 1, 1, 3)

        # Standard-dependent sub-selector (only the active one is shown)
        self.lbl_quality_level = QLabel(self.trans.get("quality_level"))
        self.cmb_quality_level = QComboBox()
        self.cmb_quality_level.addItems(["B", "C", "D"])
        self.cmb_quality_level.setCurrentIndex(1)
        self.lbl_b31_service = QLabel(self.trans.get("b31_service"))
        self.cmb_b31_service = QComboBox()
        self.cmb_b31_service.addItem(self.trans.get("service_normal"), "normal")
        self.cmb_b31_service.addItem(self.trans.get("service_severe"), "severe")
        self.lbl_viii_mode = QLabel(self.trans.get("viii_mode"))
        self.cmb_viii_mode = QComboBox()
        self.cmb_viii_mode.addItem(self.trans.get("mode_uw51"), "UW-51")
        self.cmb_viii_mode.addItem(self.trans.get("mode_uw52"), "UW-52")
        for lbl in (self.lbl_quality_level, self.lbl_b31_service, self.lbl_viii_mode):
            defect_layout.addWidget(lbl, 1, 0)
        for cmb in (self.cmb_quality_level, self.cmb_b31_service, self.cmb_viii_mode):
            defect_layout.addWidget(cmb, 1, 1, 1, 3)

        defect_layout.addWidget(QLabel(self.trans.get("defect_type")), 2, 0)
        self.cmb_defect_type = QComboBox()
        self.cmb_defect_type.addItems([
            self.trans.get("defect_ip"),
            self.trans.get("defect_if"),
            self.trans.get("defect_ic"),
            self.trans.get("defect_porosity"),
            self.trans.get("defect_crack"),
            self.trans.get("defect_slag"),
            self.trans.get("defect_undercut"),
            self.trans.get("defect_burn_through"),
        ])
        defect_layout.addWidget(self.cmb_defect_type, 2, 1, 1, 3)

        defect_layout.addWidget(QLabel(self.trans.get("defect_length")), 3, 0)
        self.txt_defect_length = QLineEdit("10.0")
        self.txt_defect_length.setValidator(QDoubleValidator(0.0, 1000.0, 2))
        defect_layout.addWidget(self.txt_defect_length, 3, 1)
        defect_layout.addWidget(QLabel(self.trans.get("defect_width")), 3, 2)
        self.txt_defect_width = QLineEdit("1.5")
        self.txt_defect_width.setValidator(QDoubleValidator(0.0, 100.0, 2))
        defect_layout.addWidget(self.txt_defect_width, 3, 3)
        defect_layout.addWidget(QLabel(self.trans.get("accumulated_12in")), 4, 0)
        self.txt_defect_accum = QLineEdit("15.0")
        self.txt_defect_accum.setValidator(QDoubleValidator(0.0, 300.0, 2))
        defect_layout.addWidget(self.txt_defect_accum, 4, 1, 1, 3)
        self.btn_eval_defect = QPushButton(self.trans.get("evaluate_defect"))
        self.btn_eval_defect.clicked.connect(self.evaluate_defect)
        defect_layout.addWidget(self.btn_eval_defect, 5, 0, 1, 4)
        self.lbl_defect_result = QLabel("")
        self.lbl_defect_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_defect_result.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
        defect_layout.addWidget(self.lbl_defect_result, 6, 0, 1, 4)
        self.tab_extra.addTab(tab_defect, self.trans.get("defect_section"))
        self._on_defect_standard_changed()

    def _on_defect_standard_changed(self):
        standard = self.cmb_defect_standard.currentData()
        self.lbl_quality_level.setVisible(standard == "iso5817")
        self.cmb_quality_level.setVisible(standard == "iso5817")
        self.lbl_b31_service.setVisible(standard == "b31_3")
        self.cmb_b31_service.setVisible(standard == "b31_3")
        self.lbl_viii_mode.setVisible(standard == "viii")
        self.cmb_viii_mode.setVisible(standard == "viii")

    def _retranslate_defect_panel(self):
        defect_idx = self.cmb_defect_type.currentIndex()
        self.cmb_defect_type.clear()
        self.cmb_defect_type.addItems([
            self.trans.get("defect_ip"),
            self.trans.get("defect_if"),
            self.trans.get("defect_ic"),
            self.trans.get("defect_porosity"),
            self.trans.get("defect_crack"),
            self.trans.get("defect_slag"),
            self.trans.get("defect_undercut"),
            self.trans.get("defect_burn_through"),
        ])
        self.cmb_defect_type.setCurrentIndex(defect_idx)
        self.btn_eval_defect.setText(self.trans.get("evaluate_defect"))
        self.tab_extra.setTabText(0, self.trans.get("defect_section"))
        # Defect standard / sub-selectors
        std_idx = self.cmb_defect_standard.currentIndex()
        self.cmb_defect_standard.clear()
        self.cmb_defect_standard.addItem(self.trans.get("defect_std_api1104"), "api1104")
        self.cmb_defect_standard.addItem(self.trans.get("defect_std_iso5817"), "iso5817")
        self.cmb_defect_standard.addItem(self.trans.get("defect_std_b31_3"), "b31_3")
        self.cmb_defect_standard.addItem(self.trans.get("defect_std_viii"), "viii")
        self.cmb_defect_standard.setCurrentIndex(std_idx)
        self.lbl_quality_level.setText(self.trans.get("quality_level"))
        s_idx = self.cmb_b31_service.currentIndex()
        self.lbl_b31_service.setText(self.trans.get("b31_service"))
        self.cmb_b31_service.clear()
        self.cmb_b31_service.addItem(self.trans.get("service_normal"), "normal")
        self.cmb_b31_service.addItem(self.trans.get("service_severe"), "severe")
        self.cmb_b31_service.setCurrentIndex(s_idx)
        m_idx = self.cmb_viii_mode.currentIndex()
        self.lbl_viii_mode.setText(self.trans.get("viii_mode"))
        self.cmb_viii_mode.clear()
        self.cmb_viii_mode.addItem(self.trans.get("mode_uw51"), "UW-51")
        self.cmb_viii_mode.addItem(self.trans.get("mode_uw52"), "UW-52")
        self.cmb_viii_mode.setCurrentIndex(m_idx)
        self._on_defect_standard_changed()
