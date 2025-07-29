# -*- coding: utf-8 -*-
"""
UI Improvements for RC Design Program
Improves label visibility and responsive design
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from language_manager import lang_manager
# from input_validation import input_validator  # Currently not available

class UIImprovements:
    """Class to improve UI label visibility and responsive design"""
    
    @staticmethod
    def improve_label_styling(label):
        """Improve label styling for better visibility"""
        # Set minimum height for better text display
        label.setMinimumHeight(22)
        
        # Improve font settings
        font = label.font()
        font.setPointSize(10)  # Increased from 9 to 10
        font.setBold(True)     # Make labels bold for better visibility
        label.setFont(font)
        
        # Better styling for labels with improved contrast
        label.setStyleSheet("""
            QLabel {
                background-color: rgb(52, 73, 94);
                color: rgb(255, 255, 255);
                border: 2px solid rgb(149, 165, 166);
                border-radius: 4px;
                padding: 3px 6px;
                font-weight: bold;
                text-align: center;
            }
        """)
        
        # Ensure alignment
        label.setAlignment(QtCore.Qt.AlignCenter)
    
    @staticmethod
    def improve_input_styling(input_widget):
        """Improve input field styling"""
        input_widget.setMinimumHeight(24)  # Increased from 22 to 24
        input_widget.setStyleSheet("""
            QLineEdit, QComboBox {
                background-color: rgb(255, 255, 255);
                border: 2px solid rgb(189, 195, 199);
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 10pt;
                font-weight: normal;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid rgb(52, 152, 219);
                background-color: rgb(250, 250, 250);
            }
            QLineEdit:hover, QComboBox:hover {
                border: 2px solid rgb(52, 152, 219);
            }
        """)
        
        # Add helpful placeholders if the field doesn't have one
        if isinstance(input_widget, QtWidgets.QLineEdit):
            object_name = input_widget.objectName()
            if not input_widget.placeholderText():
                # Add appropriate placeholders based on the field name
                if 'width' in object_name.lower() or 'b' in object_name.lower():
                    input_widget.setPlaceholderText("กว้าง (cm)")
                elif 'depth' in object_name.lower() or 'd' in object_name.lower():
                    input_widget.setPlaceholderText("ลึก (cm)")
                elif 'fc' in object_name.lower():
                    input_widget.setPlaceholderText("กก./ตร.ซม.")
                elif 'fy' in object_name.lower():
                    input_widget.setPlaceholderText("กก./ตร.ซม.")
                elif 'mu' in object_name.lower():
                    input_widget.setPlaceholderText("ตัน-ม.")
                elif 'vu' in object_name.lower() or 'vg' in object_name.lower():
                    input_widget.setPlaceholderText("ตัน")
                elif 'tu' in object_name.lower():
                    input_widget.setPlaceholderText("ตัน-ม.")
                elif 'pu' in object_name.lower():
                    input_widget.setPlaceholderText("ตัน")
                elif 'span' in object_name.lower() or 'l' == object_name.lower():
                    input_widget.setPlaceholderText("ระยะ (cm)")
                elif 'hf' in object_name.lower():
                    input_widget.setPlaceholderText("หนา (cm)")
                elif any(x in object_name.lower() for x in ['barnum', 'num']):
                    input_widget.setPlaceholderText("จำนวน")
                else:
                    input_widget.setPlaceholderText("กรอกค่า")
    
    @staticmethod
    def apply_form_improvements(form_layout):
        """Apply improvements to entire form layout"""
        # Set better spacing
        form_layout.setVerticalSpacing(8)
        form_layout.setHorizontalSpacing(10)
        
        # Improve form margins
        form_layout.setContentsMargins(5, 5, 5, 5)
    
    @staticmethod
    def apply_comprehensive_improvements(ui_window):
        """Apply comprehensive improvements to the UI window"""
        # Find all labels and improve them
        labels = ui_window.findChildren(QtWidgets.QLabel)
        for label in labels:
            # Skip labels that are likely part of drawings or special widgets
            if hasattr(label, 'objectName') and label.objectName():
                if not any(skip in label.objectName().lower() for skip in ['widget', 'drawing', 'canvas']):
                    UIImprovements.improve_label_styling(label)
        
        # Find all input fields and improve them  
        line_edits = ui_window.findChildren(QtWidgets.QLineEdit)
        for line_edit in line_edits:
            UIImprovements.improve_input_styling(line_edit)
            
        combo_boxes = ui_window.findChildren(QtWidgets.QComboBox)
        for combo_box in combo_boxes:
            UIImprovements.improve_input_styling(combo_box)
            
        # Find all buttons and improve them
        buttons = ui_window.findChildren(QtWidgets.QPushButton)
        for button in buttons:
            UIImprovements.improve_button_styling(button)
        
        # Find all form layouts and improve them
        form_layouts = ui_window.findChildren(QtWidgets.QFormLayout)
        for form_layout in form_layouts:
            UIImprovements.apply_form_improvements(form_layout)
            
        # Improve overall window responsiveness
        UIImprovements.improve_window_responsiveness(ui_window)
    
    @staticmethod
    def improve_button_styling(button):
        """Improve button styling for better appearance"""
        button.setMinimumHeight(32)
        
        # Get button text to determine styling
        button_text = button.text().lower()
        
        # Different styles for different button types
        if any(word in button_text for word in ['calculate', 'คำนวณ', 'design', 'ออกแบบ']):
            # Primary action buttons
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(231, 126, 35);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(211, 84, 0);
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 11pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgb(241, 148, 74);
                }
                QPushButton:pressed {
                    background-color: rgb(211, 84, 0);
                }
            """)
        elif any(word in button_text for word in ['back', 'กลับ', 'close', 'ปิด']):
            # Secondary action buttons
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(149, 165, 166);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(127, 140, 141);
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 10pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgb(174, 182, 191);
                }
                QPushButton:pressed {
                    background-color: rgb(127, 140, 141);
                }
            """)
        else:
            # Default button styling
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(52, 152, 219);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(41, 128, 185);
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 10pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgb(74, 168, 235);
                }
                QPushButton:pressed {
                    background-color: rgb(41, 128, 185);
                }
            """)
    
    @staticmethod
    def improve_window_responsiveness(ui_window):
        """Improve window responsiveness and layout"""
        # Set minimum window size for better visibility
        ui_window.setMinimumSize(QtCore.QSize(520, 650))
        
        # Add proper window title based on the class name
        window_title = "โปรแกรมออกแบบคอนกรีตเสริมเหล็ก"
        class_name = ui_window.__class__.__name__
        
        if "RCRecbeamCal" in str(type(ui_window)) or "recbeam" in class_name.lower():
            window_title += " - คำนวณคานสี่เหลี่ยม"
        elif "RCBeamDsgn" in str(type(ui_window)) or "beamdsgn" in class_name.lower():
            window_title += " - ออกแบบเหล็กเสริมคาน"
        elif "RCColumnCal" in str(type(ui_window)) or "column" in class_name.lower():
            window_title += " - คำนวณเสา"
        elif "RCTbeamCal" in str(type(ui_window)) or "tbeam" in class_name.lower():
            window_title += " - คำนวณคาน T"
        else:
            window_title += " - เมนูหลัก"
            
        ui_window.setWindowTitle(window_title)
        
        # Enable high DPI support
        try:
            ui_window.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            ui_window.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        except:
            pass  # Ignore if attributes are not available
        
        # Improve window appearance
        ui_window.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        
        # Set window icon if exists
        try:
            icon = QtGui.QIcon("icons/app_icon.png")
            if not icon.isNull():
                ui_window.setWindowIcon(icon)
        except:
            pass
        
        # Add keyboard navigation improvements
        ui_window.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        # Ensure proper tab order for better navigation
        widgets = ui_window.findChildren(QtWidgets.QWidget)
        focusable_widgets = [w for w in widgets if w.focusPolicy() != QtCore.Qt.NoFocus and w.isVisible()]
        
        if len(focusable_widgets) > 1:
            for i in range(len(focusable_widgets) - 1):
                ui_window.setTabOrder(focusable_widgets[i], focusable_widgets[i + 1])
                
        # Add title label at the top of the window
        UIImprovements.add_title_header(ui_window)
    
    @staticmethod
    def add_title_header(ui_window):
        """Add a title header to the window"""
        try:
            # Find the central widget
            central_widget = None
            if hasattr(ui_window, 'centralwidget'):
                central_widget = ui_window.centralwidget
            elif hasattr(ui_window, 'centralWidget'):
                central_widget = ui_window.centralWidget()
            
            if central_widget:
                # Create title label
                title_label = QtWidgets.QLabel(central_widget)
                title_label.setObjectName("title_header")
                
                # Set title text based on window type
                title_text = "โปรแกรมออกแบบคอนกรีตเสริมเหล็ก"
                class_name = ui_window.__class__.__name__
                
                if "RCRecbeamCal" in str(type(ui_window)) or "recbeam" in class_name.lower():
                    title_text = "คำนวณความแข็งแรงคานสี่เหลี่ยม"
                elif "RCBeamDsgn" in str(type(ui_window)) or "beamdsgn" in class_name.lower():
                    title_text = "ออกแบบเหล็กเสริมคาน"
                elif "RCColumnCal" in str(type(ui_window)) or "column" in class_name.lower():
                    title_text = "คำนวณความแข็งแรงเสา"
                elif "RCTbeamCal" in str(type(ui_window)) or "tbeam" in class_name.lower():
                    title_text = "คำนวณความแข็งแรงคาน T"
                
                title_label.setText(title_text)
                
                # Style the title label
                title_label.setStyleSheet("""
                    QLabel {
                        background-color: rgb(44, 62, 80);
                        color: rgb(255, 255, 255);
                        border: 2px solid rgb(52, 73, 94);
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 14pt;
                        font-weight: bold;
                        text-align: center;
                    }
                """)
                
                # Position the title at the top
                title_label.setGeometry(10, 10, central_widget.width() - 20, 40)
                title_label.setAlignment(QtCore.Qt.AlignCenter)
                title_label.show()
                
                # Move other widgets down to make space for title
                widgets = central_widget.findChildren(QtWidgets.QWidget)
                for widget in widgets:
                    if widget != title_label and hasattr(widget, 'geometry'):
                        geom = widget.geometry()
                        if geom.y() < 60:  # If widget is in the title area
                            widget.setGeometry(geom.x(), geom.y() + 50, geom.width(), geom.height())
                            
        except Exception as e:
            # If title addition fails, continue without it
            pass

# Global UI improvements instance
ui_improvements = UIImprovements()

# Apply language manager settings
try:
    lang_manager.set_default_language("th")  # Set default language to Thai
    lang_manager.add_language("en", "English")
    lang_manager.add_language("zh", "Chinese")
    
    # Load user preferred language if available
    user_language = lang_manager.load_user_preference()
    if user_language:
        lang_manager.set_current_language(user_language)
except Exception as e:
    # If language manager fails, continue without it
    pass

# Connect language change signal to update UI
try:
    def on_language_changed(new_language):
        """Update UI language on change"""
        lang_manager.set_current_language(new_language)
        # TODO: Add code to update all translatable UI elements
        
    lang_manager.language_changed.connect(on_language_changed)
except Exception as e:
    # If signal connection fails, continue without it
    pass
