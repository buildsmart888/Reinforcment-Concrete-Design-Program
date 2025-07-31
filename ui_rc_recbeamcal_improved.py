# -*- coding: utf-8 -*-
"""
Improved UI for RC Rectangular Beam Calculation
Enhanced with better design, validation, and user experience
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from widget_rc_recbeam import RcRecBeamWidget
import icons_rc
from language_manager import lang_manager
from simple_ui_helper import simple_ui_helper


class ModernLineEdit(QtWidgets.QLineEdit):
    """Custom line edit with modern styling and validation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_styling()
        self.textChanged.connect(self.validate_input)
        
    def setup_styling(self):
        """Apply modern styling to the line edit"""
        self.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #e0e6ed;
                border-radius: 8px;
                padding: 16px 20px;  /* เพิ่ม padding เพื่อให้ช่องกรอกใหญ่ขึ้น */
                font-size: 16px;      /* เพิ่มขนาดฟอนต์ */
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2c3e50;
                selection-background-color: #3498db;
                min-height: 25px;     /* กำหนดความสูงขั้นต่ำ */
                min-width: 300px;     /* เพิ่มความกว้างขั้นต่ำให้มากขึ้นอีก */
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f8fafb;
            }
            QLineEdit:hover {
                border-color: #bdc3c7;
                background-color: #f8fafb;
            }
            QLineEdit[error="true"] {
                border-color: #e74c3c;
                background-color: #fdf2f2;
            }
        """)
        
        # Add shadow effect (removed - not supported by Qt)
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(10)
        # shadow.setXOffset(0)
        # shadow.setYOffset(2)
        # shadow.setColor(QtGui.QColor(0, 0, 0, 30))
        # self.setGraphicsEffect(shadow)
    
    def validate_input(self):
        """Validate numeric input"""
        text = self.text()
        if text and not self.is_valid_number(text):
            self.setProperty("error", True)
        else:
            self.setProperty("error", False)
        self.style().unpolish(self)
        self.style().polish(self)
    
    def is_valid_number(self, text):
        """Check if text is a valid positive number"""
        try:
            value = float(text)
            return value > 0
        except ValueError:
            return False


class ModernLabel(QtWidgets.QLabel):
    """Custom label with modern styling"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setup_styling()
    
    def setup_styling(self):
        """Apply modern styling to the label"""
        self.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
                padding: 8px 0px;
            }
        """)


class ModernButton(QtWidgets.QPushButton):
    """Custom button with modern styling and animations"""
    
    def __init__(self, text, button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_styling()
        self.setup_animation()
    
    def setup_styling(self):
        """Apply modern styling based on button type"""
        if self.button_type == "primary":
            style = """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 14px 28px;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
                QPushButton:disabled {
                    background-color: #bdc3c7;
                    color: #7f8c8d;
                }
            """
        elif self.button_type == "success":
            style = """
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 14px 28px;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
            """
        elif self.button_type == "info":
            style = """
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 14px 28px;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
                QPushButton:pressed {
                    background-color: #0f6674;
                }
            """
        else:  # secondary
            style = """
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 14px 28px;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
                QPushButton:pressed {
                    background-color: #495057;
                }
            """
        
        self.setStyleSheet(style)
        
        # Add shadow effect (removed - not supported by Qt)
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(15)
        # shadow.setXOffset(0)
        # shadow.setYOffset(3)
        # shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        # self.setGraphicsEffect(shadow)
    
    def setup_animation(self):
        """Setup hover animations"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def enterEvent(self, event):
        """Handle mouse enter event"""
        super().enterEvent(event)
        # Add subtle scale effect
        self.setCursor(QtCore.Qt.PointingHandCursor)
    
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        super().leaveEvent(event)
        self.setCursor(QtCore.Qt.ArrowCursor)


class ModernGroupBox(QtWidgets.QGroupBox):
    """Custom group box with modern styling"""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setup_styling()
    
    def setup_styling(self):
        """Apply modern styling to the group box"""
        self.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2c3e50;
                border: 2px solid #ecf0f1;
                border-radius: 12px;
                margin-top: 12px;
                padding: 15px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: #ffffff;
                color: #2c3e50;
            }
        """)
        
        # Add shadow effect (removed - not supported by Qt)
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(20)
        # shadow.setXOffset(0)
        # shadow.setYOffset(4)
        # shadow.setColor(QtGui.QColor(0, 0, 0, 20))
        # self.setGraphicsEffect(shadow)


class Ui_RcRecBeamCalImproved(object):
    """Improved UI class for RC Rectangular Beam Calculation"""
    
    def setupUi(self, RCRecbeamCal):
        RCRecbeamCal.setObjectName("RCRecbeamCalImproved")
        RCRecbeamCal.resize(2000, 1200)  # เพิ่มขนาดให้ใหญ่ขึ้นอีก
        RCRecbeamCal.setMinimumSize(1800, 1100)  # เพิ่มขนาดขั้นต่ำ
        
        # Set window title and ensure standard window controls
        RCRecbeamCal.setWindowTitle("โปรแกรมออกแบบคานคอนกรีตเสริมเหล็ก - Rectangular Beam Design")
        
        # Set modern window style
        RCRecbeamCal.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        
        self.centralwidget = QtWidgets.QWidget(RCRecbeamCal)
        self.centralwidget.setObjectName("centralwidget")
        
        # Create main layout with better spacing and proportions
        main_layout = QtWidgets.QHBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(10, 10, 10, 10)  # ลด margins เพื่อให้มีพื้นที่มากขึ้น
        main_layout.setSpacing(20)
        
        # Left panel - Input controls (ลด proportion)
        self.setup_input_panel(main_layout)
        
        # Right panel - Output and visualization (เพิ่ม proportion)
        self.setup_output_panel(main_layout)
        
        RCRecbeamCal.setCentralWidget(self.centralwidget)
        
        # Create status bar
        self.statusbar = QtWidgets.QStatusBar(RCRecbeamCal)
        self.statusbar.setObjectName("statusbar")
        RCRecbeamCal.setStatusBar(self.statusbar)
        
        # Apply translations
        self.retranslateUi(RCRecbeamCal)
        QtCore.QMetaObject.connectSlotsByName(RCRecbeamCal)
    
    def setup_input_panel(self, main_layout):
        """Setup the left input panel with improved design and better visibility"""
        # Create scroll area for inputs with better proportions
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumWidth(750)  # ขยายความกว้างให้มากขึ้นอีก
        scroll_area.setMinimumWidth(700)  # เพิ่มความกว้างขั้นต่ำ
        scroll_area.setMinimumHeight(900)  # กำหนดความสูงขั้นต่ำเพื่อให้เห็นปุ่มครบ
        # กำหนดให้เลื่อนได้แค่แนวตั้งเท่านั้น
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #ffffff;
            }
        """)
        
        input_widget = QtWidgets.QWidget()
        input_layout = QtWidgets.QVBoxLayout(input_widget)
        input_layout.setSpacing(20)  # ลดระยะห่างเล็กน้อยเพื่อประหยัดพื้นที่
        input_layout.setContentsMargins(20, 20, 20, 20)  # ลด margins เล็กน้อย
        
        # Section 1: Beam Dimensions
        self.setup_dimensions_section(input_layout)
        
        # Section 2: Material Properties
        self.setup_materials_section(input_layout)
        
        # Section 3: Reinforcement Details
        self.setup_reinforcement_section(input_layout)
        
        # Section 4: Loading
        self.setup_loading_section(input_layout)
        
        # Section 4: Action Buttons
        self.setup_action_buttons(input_layout)
        
        # ลบ addStretch() เพื่อไม่ให้ปุ่มถูกดันไปไกล
        
        scroll_area.setWidget(input_widget)
        main_layout.addWidget(scroll_area, 0)  # ลดให้ไม่ยืดตาม weight
    
    def setup_dimensions_section(self, parent_layout):
        """Setup beam dimensions input section with improved visibility"""
        dimensions_group = ModernGroupBox("ข้อมูลมิติคาน")
        layout = QtWidgets.QFormLayout()
        layout.setSpacing(16)  # เพิ่มระยะห่าง
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.setFormAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        
        # Beam width
        self.label_width = ModernLabel("ความกว้างคาน B (มม.)")
        self.width = ModernLineEdit()
        self.width.setPlaceholderText("เช่น 300")
        self.width.setText("300")
        self.width.setMinimumWidth(280)  # เพิ่มความกว้างขั้นต่ำ
        layout.addRow(self.label_width, self.width)
        
        # Beam depth
        self.label_depth = ModernLabel("ความสูงคาน H (มม.)")
        self.depth = ModernLineEdit()
        self.depth.setPlaceholderText("เช่น 500")
        self.depth.setText("500")
        self.depth.setMinimumWidth(280)
        layout.addRow(self.label_depth, self.depth)
        
        # Effective depth - ไม่ต้องกรอก จะคำนวณอัตโนมัติ
        self.label_d = ModernLabel("ความลึกมีประสิทธิภาพ d (มม.) - คำนวณอัตโนมัติ")
        self.d_display = ModernLabel("จะคำนวณจากความสูง - ระยะหุ้ม - ขนาดเหล็ก")
        self.d_display.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 15px;
                font-weight: 600;
                font-style: italic;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f8f9fa;
                border: 2px solid #27ae60;
                border-radius: 8px;
                padding: 14px 18px;
                min-height: 20px;
                min-width: 280px;  /* เพิ่มความกว้างให้สอดคล้องกับช่องอื่น */
            }
        """)
        layout.addRow(self.label_d, self.d_display)
        
        # Clear cover
        self.label_cover = ModernLabel("ระยะหุ้ม (มม.)")
        self.cover = ModernLineEdit()
        self.cover.setPlaceholderText("เช่น 40")
        self.cover.setText("40")
        self.cover.setMinimumWidth(280)
        layout.addRow(self.label_cover, self.cover)
        
        # ลบความยาวคานออก - ตามที่ผู้ใช้ร้องขอ
        
        dimensions_group.setLayout(layout)
        parent_layout.addWidget(dimensions_group)
    
    def setup_materials_section(self, parent_layout):
        """Setup material properties input section with improved visibility"""
        materials_group = ModernGroupBox("คุณสมบัติวัสดุ")
        layout = QtWidgets.QFormLayout()
        layout.setSpacing(16)  # เพิ่มระยะห่าง
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.setFormAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        
        # Concrete strength
        self.label_fc = ModernLabel("กำลังรับแรงอัดคอนกรีต f'c (ksc)")
        self.fc = ModernLineEdit()
        self.fc.setPlaceholderText("เช่น 245")
        self.fc.setText("245.00")
        self.fc.setMinimumWidth(220)
        layout.addRow(self.label_fc, self.fc)
        
        # Steel strength
        self.label_fy = ModernLabel("กำลังรับแรงเหล็กเสริม fy (ksc)")
        self.fy = ModernLineEdit()
        self.fy.setPlaceholderText("เช่น 4000")
        self.fy.setText("4000.00")
        self.fy.setMinimumWidth(220)
        layout.addRow(self.label_fy, self.fy)
        
        materials_group.setLayout(layout)
        parent_layout.addWidget(materials_group)
    
    def setup_reinforcement_section(self, parent_layout):
        """Setup reinforcement details input section"""
        rebar_group = ModernGroupBox("ข้อมูลเหล็กเสริม")
        layout = QtWidgets.QFormLayout()
        layout.setSpacing(12)  # ลดระยะห่างจาก 15 เป็น 12
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        
        # Main reinforcement (tension)
        self.label_main_rebar = ModernLabel("เหล็กรับแรงดึง")
        main_rebar_layout = QtWidgets.QHBoxLayout()
        
        self.main_rebar_size = QtWidgets.QComboBox()
        self.main_rebar_size.addItems(['#3(D10)', '#4(D13)', '#5(D16)', '#6(D19)', 
                                      '#7(D22)', '#8(D25)', '#9(D29)', '#10(D32)', '#11(D36)'])
        self.main_rebar_size.setCurrentText('#5(D16)')
        self.main_rebar_size.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #e0e6ed;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        
        self.main_rebar_num = ModernLineEdit()
        self.main_rebar_num.setPlaceholderText("จำนวน")
        self.main_rebar_num.setText("4")
        self.main_rebar_num.setMinimumWidth(100)
        self.main_rebar_num.setMaximumWidth(120)
        
        label_x = QtWidgets.QLabel("x")
        label_x.setAlignment(QtCore.Qt.AlignCenter)
        label_x.setMinimumWidth(20)
        
        main_rebar_layout.addWidget(self.main_rebar_size, 3)
        main_rebar_layout.addWidget(label_x, 0)
        main_rebar_layout.addWidget(self.main_rebar_num, 2)
        layout.addRow(self.label_main_rebar, main_rebar_layout)
        
        # Compression reinforcement
        self.label_comp_rebar = ModernLabel("เหล็กรับแรงอัด")
        comp_rebar_layout = QtWidgets.QHBoxLayout()
        
        self.comp_rebar_size = QtWidgets.QComboBox()
        self.comp_rebar_size.addItems(['#3(D10)', '#4(D13)', '#5(D16)', '#6(D19)', 
                                      '#7(D22)', '#8(D25)', '#9(D29)', '#10(D32)', '#11(D36)'])
        self.comp_rebar_size.setCurrentText('#4(D13)')
        self.comp_rebar_size.setStyleSheet(self.main_rebar_size.styleSheet())
        
        self.comp_rebar_num = ModernLineEdit()
        self.comp_rebar_num.setPlaceholderText("จำนวน")
        self.comp_rebar_num.setText("2")
        self.comp_rebar_num.setMinimumWidth(100)
        self.comp_rebar_num.setMaximumWidth(120)
        
        label_x2 = QtWidgets.QLabel("x")
        label_x2.setAlignment(QtCore.Qt.AlignCenter)
        label_x2.setMinimumWidth(20)
        
        comp_rebar_layout.addWidget(self.comp_rebar_size, 3)
        comp_rebar_layout.addWidget(label_x2, 0)
        comp_rebar_layout.addWidget(self.comp_rebar_num, 2)
        layout.addRow(self.label_comp_rebar, comp_rebar_layout)
        
        # Stirrup details
        self.label_stirrup = ModernLabel("เหล็กปลอก")
        stirrup_layout = QtWidgets.QHBoxLayout()
        
        self.stirrup_size = QtWidgets.QComboBox()
        self.stirrup_size.addItems(['#3(D10)', '#4(D13)', '#5(D16)', '#6(D19)'])
        self.stirrup_size.setCurrentText('#3(D10)')
        self.stirrup_size.setStyleSheet(self.main_rebar_size.styleSheet())
        
        self.stirrup_type = QtWidgets.QComboBox()
        self.stirrup_type.addItems(['เหล็กปลอกสองขา', 'เหล็กปลอกสามขา', 'เหล็กปลอกสี่ขา'])
        self.stirrup_type.setCurrentText('เหล็กปลอกสองขา')
        self.stirrup_type.setStyleSheet(self.main_rebar_size.styleSheet())
        
        stirrup_layout.addWidget(self.stirrup_size, 1)
        stirrup_layout.addWidget(self.stirrup_type, 2)
        layout.addRow(self.label_stirrup, stirrup_layout)
        
        # Stirrup spacing
        self.label_stirrup_spacing = ModernLabel("ระยะห่างเหล็กปลอก (มม.)")
        self.stirrup_spacing = ModernLineEdit()
        self.stirrup_spacing.setPlaceholderText("เช่น 150")
        self.stirrup_spacing.setText("150")
        layout.addRow(self.label_stirrup_spacing, self.stirrup_spacing)
        
        rebar_group.setLayout(layout)
        parent_layout.addWidget(rebar_group)
    
    def setup_loading_section(self, parent_layout):
        """Setup loading input section"""
        loading_group = ModernGroupBox("แรงกระทำ")
        layout = QtWidgets.QFormLayout()
        layout.setSpacing(12)  # ลดระยะห่างจาก 15 เป็น 12
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        
        # Moment
        self.label_moment = ModernLabel("โมเมนต์ Mu (ตัน-เมตร)")
        self.moment = ModernLineEdit()
        self.moment.setPlaceholderText("เช่น 15")
        self.moment.setText("15.00")
        layout.addRow(self.label_moment, self.moment)
        
        # Shear force
        self.label_shear = ModernLabel("แรงเฉือน Vu (ตัน)")
        self.shear = ModernLineEdit()
        self.shear.setPlaceholderText("เช่น 8")
        self.shear.setText("8.00")
        layout.addRow(self.label_shear, self.shear)
        
        # ลบโมเมนต์บิด Tu ออกแล้ว
        
        loading_group.setLayout(layout)
        parent_layout.addWidget(loading_group)
    
    def setup_action_buttons(self, parent_layout):
        """Setup action buttons with better spacing and visibility"""
        buttons_group = ModernGroupBox("การดำเนินการ")
        buttons_group.setMinimumHeight(280)  # กำหนดความสูงขั้นต่ำให้มากขึ้น
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(12)  # เพิ่มระยะห่างระหว่างปุ่ม
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Calculate button (ปุ่มหลัก - ขนาดใหญ่)
        self.btn_calculate = ModernButton("🧮 คำนวณ", "primary")
        self.btn_calculate.setIcon(QtGui.QIcon(":/icons/calculator.png"))
        self.btn_calculate.setMinimumHeight(55)  # เพิ่มความสูงของปุ่มหลัก
        self.btn_calculate.setStyleSheet(self.btn_calculate.styleSheet() + "font-size: 16px; font-weight: bold;")
        layout.addWidget(self.btn_calculate)
        
        # สร้าง horizontal layout สำหรับปุ่มรอง
        row1_layout = QtWidgets.QHBoxLayout()
        row1_layout.setSpacing(8)
        
        # Clear button
        self.btn_clear = ModernButton("🗑️ ล้างข้อมูล", "secondary")
        self.btn_clear.setIcon(QtGui.QIcon(":/icons/clear.png"))
        self.btn_clear.setMinimumHeight(48)
        self.btn_clear.setMinimumWidth(180)  # กำหนดความกว้างขั้นต่ำ
        row1_layout.addWidget(self.btn_clear)
        
        # Export PDF button
        self.btn_export_pdf = ModernButton("📄 ส่งออก", "info")
        self.btn_export_pdf.setIcon(QtGui.QIcon(":/icons/pdf.png"))
        self.btn_export_pdf.setMinimumHeight(48)
        self.btn_export_pdf.setMinimumWidth(180)  # กำหนดความกว้างขั้นต่ำ
        self.btn_export_pdf.setToolTip("ส่งออกรายงาน PDF")  # เพิ่ม tooltip
        row1_layout.addWidget(self.btn_export_pdf)
        
        layout.addLayout(row1_layout)
        
        # Save data button
        self.btn_save = ModernButton("💾 บันทึกข้อมูล", "success")
        self.btn_save.setIcon(QtGui.QIcon(":/icons/save.png"))
        self.btn_save.setMinimumHeight(48)
        layout.addWidget(self.btn_save)
        
        buttons_group.setLayout(layout)
        parent_layout.addWidget(buttons_group)
        
        # ลบ spacer เพื่อให้ปุ่มอยู่ติดกัน ไม่มีพื้นที่ว่างมาก
    
    def setup_output_panel(self, main_layout):
        """Setup the right output panel"""
        # Create tab widget for different output views
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #bdc3c7;
            }
        """)
        
        # Results tab
        self.setup_results_tab()
        
        # Visualization tab
        self.setup_visualization_tab()
        
        # Report tab
        self.setup_report_tab()
        
        main_layout.addWidget(self.tab_widget, 2)  # Give more space to output
    
    def setup_results_tab(self):
        """Setup results display tab"""
        results_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(results_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Results text area with modern styling
        self.results_text = QtWidgets.QTextEdit()
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 16px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                line-height: 1.5;
                color: #2c3e50;
            }
        """)
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)
        
        self.tab_widget.addTab(results_widget, "ผลลัพธ์การคำนวณ")
    
    def setup_visualization_tab(self):
        """Setup visualization tab"""
        viz_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(viz_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Placeholder for matplotlib widget
        self.plot_widget = RcRecBeamWidget()
        layout.addWidget(self.plot_widget)
        
        self.tab_widget.addTab(viz_widget, "แผนภาพ")
    
    def setup_report_tab(self):
        """Setup report tab"""
        report_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(report_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Report text area
        self.report_text = QtWidgets.QTextEdit()
        self.report_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                line-height: 1.6;
                color: #2c3e50;
            }
        """)
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)
        
        self.tab_widget.addTab(report_widget, "รายงานผล")
    
    def retranslateUi(self, RCRecbeamCal):
        """Apply translations using language manager"""
        _translate = QtCore.QCoreApplication.translate
        
        # Get current language
        current_lang = lang_manager.current_language
        
        # Set window title
        if current_lang == 'en':
            RCRecbeamCal.setWindowTitle("RC BEAM Analysis SKC.V.1.0.alpha")
        elif current_lang == 'zh':
            RCRecbeamCal.setWindowTitle("RC BEAM Analysis SKC.V.1.0.alpha")
        else:  # Thai
            RCRecbeamCal.setWindowTitle("RC BEAM Analysis SKC.V.1.0.alpha")
        
        # Update all text elements based on language
        self.update_language_texts()
    
    def update_language_texts(self):
        """Update all text elements based on current language"""
        lang = lang_manager.current_language
        
        # This method would be called when language changes
        # Implementation would update all labels, buttons, etc.
        pass


class ModernInputValidator:
    """Input validation helper class"""
    
    @staticmethod
    def validate_positive_number(text, min_value=0.01, max_value=None):
        """Validate positive number input"""
        try:
            value = float(text)
            if value < min_value:
                return False, f"ค่าต้องมากกว่า {min_value}"
            if max_value and value > max_value:
                return False, f"ค่าต้องน้อยกว่า {max_value}"
            return True, ""
        except ValueError:
            return False, "กรุณาใส่ตัวเลขที่ถูกต้อง"
    
    @staticmethod
    def validate_positive_integer(text, min_value=1, max_value=None):
        """Validate positive integer input"""
        try:
            value = int(text)
            if value < min_value:
                return False, f"ค่าต้องมากกว่าหรือเท่ากับ {min_value}"
            if max_value and value > max_value:
                return False, f"ค่าต้องน้อยกว่าหรือเท่ากับ {max_value}"
            return True, ""
        except ValueError:
            return False, "กรุณาใส่จำนวนเต็มที่ถูกต้อง"
    
    @staticmethod
    def validate_beam_dimensions(width, depth, d, cover):
        """Validate beam dimension relationships"""
        try:
            w = float(width)
            h = float(depth)
            effective_d = float(d)
            c = float(cover)
            
            if effective_d >= h:
                return False, "ความลึกมีประสิทธิภาพต้องน้อยกว่าความสูงรวม"
            
            if w < 150:
                return False, "ความกว้างคานควรมากกว่า 150 มม."
            
            if h < 300:
                return False, "ความสูงคานควรมากกว่า 300 มม."
                
            if c < 20:
                return False, "ระยะหุ้มควรมากกว่า 20 มม."
                
            if c > h/4:
                return False, "ระยะหุ้มมากเกินไป"
                
            expected_d = h - c
            if abs(effective_d - expected_d) > c:
                return False, f"ความลึกมีประสิทธิภาพควรอยู่ใกล้ {expected_d:.0f} มม."
            
            return True, ""
        except ValueError:
            return False, "กรุณาใส่ข้อมูลมิติที่ถูกต้อง"
    
    @staticmethod
    def validate_material_properties(fc, fy):
        """Validate material properties"""
        try:
            concrete_strength = float(fc)
            steel_strength = float(fy)
            
            if concrete_strength < 150:  # ksc (เปลี่ยนจาก 15 MPa)
                return False, "กำลังรับแรงอัดคอนกรีตต้องมากกว่า 150 ksc"
            if concrete_strength > 800:  # ksc (เปลี่ยนจาก 80 MPa)
                return False, "กำลังรับแรงอัดคอนกรีตต้องน้อยกว่า 800 ksc"
                
            if steel_strength < 2400:  # ksc (เปลี่ยนจาก 240 MPa)
                return False, "กำลังรับแรงดึงเหล็กต้องมากกว่า 2400 ksc"
            if steel_strength > 7000:  # ksc (เปลี่ยนจาก 700 MPa)
                return False, "กำลังรับแรงดึงเหล็กต้องน้อยกว่า 7000 ksc"
            
            return True, ""
        except ValueError:
            return False, "กรุณาใส่ค่าคุณสมบัติวัสดุที่ถูกต้อง"
    
    @staticmethod
    def validate_reinforcement(main_num, comp_num, stirrup_spacing):
        """Validate reinforcement details"""
        try:
            main_bars = int(main_num)
            comp_bars = int(comp_num)
            spacing = float(stirrup_spacing)
            
            if main_bars < 2:
                return False, "เหล็กรับแรงดึงต้องมีอย่างน้อย 2 เส้น"
            if main_bars > 20:
                return False, "เหล็กรับแรงดึงมากเกินไป (มากกว่า 20 เส้น)"
                
            if comp_bars < 0:
                return False, "จำนวนเหล็กรับแรงอัดต้องไม่ติดลบ"
            if comp_bars > 15:
                return False, "เหล็กรับแรงอัดมากเกินไป (มากกว่า 15 เส้น)"
                
            if spacing < 50:
                return False, "ระยะห่างเหล็กปลอกต้องมากกว่า 50 มม."
            if spacing > 600:
                return False, "ระยะห่างเหล็กปลอกต้องน้อยกว่า 600 มม."
            
            return True, ""
        except ValueError:
            return False, "กรุณาใส่ข้อมูลเหล็กเสริมที่ถูกต้อง"
    
    @staticmethod
    def validate_loading(moment, shear):
        """Validate loading conditions"""
        try:
            Mu = float(moment)
            Vu = float(shear)
            
            if Mu < 0:
                return False, "โมเมนต์ต้องไม่ติดลบ"
            if Mu > 10000:
                return False, "โมเมนต์มากเกินไป (มากกว่า 10,000 ตัน-เมตร)"
                
            if Vu < 0:
                return False, "แรงเฉือนต้องไม่ติดลบ"
            if Vu > 5000:
                return False, "แรงเฉือนมากเกินไป (มากกว่า 5,000 ตัน)"
            
            return True, ""
        except ValueError:
            return False, "กรุณาใส่ข้อมูลแรงกระทำที่ถูกต้อง"


# Usage example
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    # Apply application-wide styles
    app.setStyleSheet("""
        QApplication {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QTooltip {
            background-color: #2c3e50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px;
            font-size: 12px;
        }
    """)
    
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_RcRecBeamCalImproved()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
