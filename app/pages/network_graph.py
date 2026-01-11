from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem,
    QGraphicsItem, QPushButton, QGraphicsTextItem, QGraphicsDropShadowEffect,
    QGraphicsPolygonItem, QGraphicsRectItem, QFrame, QVBoxLayout, QLabel, QWidget,
    QGraphicsOpacityEffect
)
from PySide6.QtGui import QBrush, QPen, QColor, QPainter, QRadialGradient, QFont, QPolygonF
from PySide6.QtCore import Qt, QTimer, QPointF, QPropertyAnimation, QEasingCurve, QRectF, QUrl
import math
import random
from app.utils.audio import AudioManager





# ---------- DIRECTED EDGE (ARROW) ----------
class DirectedEdge(QGraphicsPolygonItem):
    def __init__(self, source, dest):
        super().__init__()
        self.source = source
        self.dest = dest

        self.normal_brush = QBrush(QColor("#AAAAAA"))
        self.normal_pen = QPen(QColor("#AAAAAA"), 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        #darker_purple = QColor("#4834D4")
        self.highlight_brush = QBrush(QColor("#6C5CE7"))
        self.highlight_pen = QPen(QColor("#6C5CE7"), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        self.setZValue(-1)
        self.setOpacity(0.7)

        self.line = QGraphicsLineItem(self)

        self.update_theme()
        self.update_position()

    def update_theme(self):
        self.setBrush(self.normal_brush)
        self.setPen(self.normal_pen)
        self.line.setPen(self.normal_pen)

    def highlight(self, enabled):
        if enabled:
            self.setBrush(self.highlight_brush)
            self.setPen(self.highlight_pen)
            self.line.setPen(self.highlight_pen)
            self._animate_opacity(0.7, 1.0, 5)
        else:
            self.setBrush(self.normal_brush)
            self.setPen(self.normal_pen)
            self.line.setPen(self.normal_pen)
            self._animate_opacity(1.0, 0.7, 5)

    def _animate_opacity(self, start, end, steps):
        for i in range(steps + 1):
            opacity = start + (end - start) * (i / steps)
            QTimer.singleShot(i * 20, lambda o=opacity: self.setOpacity(o))

    def update_position(self):
        start = self.source.pos()
        end = self.dest.pos()
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return

        dx /= length
        dy /= length
        target_radius = self.dest.normal_size / 2
        offset = target_radius + 2
        end_x = end.x() - dx * offset
        end_y = end.y() - dy * offset

        self.line.setLine(start.x(), start.y(), end_x, end_y)

        arrow_size = 12
        angle = math.atan2(dy, dx)
        tip = QPointF(end_x, end_y)
        p1 = QPointF(end_x - arrow_size * math.cos(angle - math.pi / 6),
                     end_y - arrow_size * math.sin(angle - math.pi / 6))
        p2 = QPointF(end_x - arrow_size * math.cos(angle + math.pi / 6),
                     end_y - arrow_size * math.sin(angle + math.pi / 6))

        arrow = QPolygonF([tip, p1, p2])
        self.setPolygon(arrow)

    def fade_to(self, target_opacity, duration=300):
        start_opacity = self.opacity()
        steps = 15
        interval = duration // steps
        for i in range(steps + 1):
            t = i / steps
            new_op = start_opacity + (target_opacity - start_opacity) * t
            QTimer.singleShot(i * interval, lambda val=new_op: self.setOpacity(val))


# ---------- NODE ----------
class Node(QGraphicsEllipseItem):
    def __init__(self, node_id, x, y, main_window=None, graph_view=None, audio_manager=None, centrality=0.0):
        # 1. Calculate Dynamic Base Size based on centrality (0.0 to 1.0)
        # Base size 50, max extra 30. An influencer will be size 80.
        self.centrality = centrality
        self.normal_size = 50 + (self.centrality * 30)

        # Center the larger node correctly
        offset = self.normal_size / 2
        super().__init__(-offset, -offset, self.normal_size, self.normal_size)

        self.setPos(x, y)
        self.main_window = main_window
        self.graph_view = graph_view
        self.audio = audio_manager

        self.velocity_x = 0
        self.velocity_y = 0
        self.is_being_dragged = False
        self.is_hovered = False

        self.id = node_id
        self.username = f"user_{node_id}"
        self.interests = []
        self.is_valid = False

        if self.main_window:
            user_data = self.main_window.app.search_user_by_id(node_id)
            if user_data:
                self.is_valid = True
                self.username = user_data.get('username', self.username)
                self.interests = user_data.get('interests', [])
            else:
                self.setVisible(False)

        self.outgoing_edges = []
        self.incoming_edges = []

        if self.is_valid:
            self.setFlags(
                QGraphicsItem.ItemIsMovable |
                QGraphicsItem.ItemSendsScenePositionChanges |
                QGraphicsItem.ItemSendsGeometryChanges
            )
            self.setAcceptHoverEvents(True)
            self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

            self.shadow = QGraphicsDropShadowEffect()
            self.shadow.setBlurRadius(15)
            self.shadow.setColor(QColor(0, 0, 0, 100))
            self.shadow.setOffset(0, 3)
            self.setGraphicsEffect(self.shadow)

            # Label
            self.label = QGraphicsTextItem(str(node_id), self)
            font = QFont("Arial", 12, QFont.Bold)
            self.label.setFont(font)
            label_rect = self.label.boundingRect()
            self.label.setPos(-label_rect.width() / 2, -label_rect.height() / 2)

            # Tooltip (Floating above node)
            self.info_bg = QGraphicsRectItem(self)
            self.info_bg.setVisible(False)
            self.info_bg.setZValue(99)
            self.info_shadow = QGraphicsDropShadowEffect()
            self.info_shadow.setBlurRadius(10)
            self.info_shadow.setColor(QColor(0, 0, 0, 80))
            self.info_shadow.setOffset(0, 2)
            self.info_bg.setGraphicsEffect(self.info_shadow)

            self.info_text = QGraphicsTextItem(self)
            # Add score to the floating tooltip
            self.info_text.setPlainText(f"@{self.username}\nInf: {int(self.centrality * 100)}%")
            info_font = QFont("Arial", 10, QFont.Bold)
            self.info_text.setFont(info_font)
            text_r = self.info_text.boundingRect()
            # Initial position, updated in update_tooltip_pos
            self.info_text.setPos(-text_r.width() / 2, -55)
            self.info_text.setVisible(False)
            self.info_text.setZValue(100)

            self.update_theme()
            self.update_tooltip_pos()

    def update_theme(self):
        if not self.is_valid: return
        dark = False
        if self.main_window and hasattr(self.main_window, 'dark_mode'):
            dark = self.main_window.dark_mode

        # Initialize Defaults
        c_start = QColor()
        c_end = QColor()
        border = QColor()
        hover_start = QColor()
        hover_end = QColor()
        hover_border = QColor()
        label_col = QColor()
        info_col = QColor()

        # --- LIGHT MODE PALETTES ---
        if not dark:
            # Common text/info colors
            label_col = QColor("white")
            info_col = QColor("#2D3436")
            self.info_bg.setBrush(QBrush(QColor(255, 255, 255, 240)))
            self.info_bg.setPen(QPen(QColor("#6C5CE7"), 2))

            if self.centrality < 0.25:
                # Level 1: Weak (Very Pale Lavender)
                c_start = QColor("#E6E6FA")
                c_end = QColor("#D1D1F0")
                border = QColor("#B0B0D0")
                label_col = QColor("#555555")

                hover_start = QColor("#F0F0FF")
                hover_end = QColor("#E0E0FF")
                hover_border = QColor("#9999BB")

            elif self.centrality < 0.50:
                # Level 2: Medium (Soft Purple)
                c_start = QColor("#D6D1F5")
                c_end = QColor("#A29BFE")
                border = QColor("#8880C0")

                hover_start = QColor("#E6E1FF")
                hover_end = QColor("#B3ACFF")
                hover_border = QColor("#9990D0")

            elif self.centrality < 0.75:
                # Level 3: ORIGINAL (Standard Purple)
                c_start = QColor("#A29BFE")
                c_end = QColor("#6C5CE7")
                border = QColor("#5948C3")

                hover_start = QColor("#B8B3FF")
                hover_end = QColor("#7E6FF2")
                hover_border = QColor("#6C5CE7")

            else:
                # Level 4: Stronger Purple (Deep Indigo) - FIX: No Red!
                c_start = QColor("#6C5CE7")  # Starts where L3 ends
                c_end = QColor("#4834D4")  # Deep Royal Indigo
                border = QColor("#30336B")  # Navy-Purple Border

                hover_start = QColor("#7E6FF2")
                hover_end = QColor("#5948C3")
                hover_border = QColor("#4834D4")

        # --- DARK MODE PALETTES ---
        else:
            # Common text/info colors
            label_col = QColor("#2D3436")
            info_col = QColor("#EDEDED")
            self.info_bg.setBrush(QBrush(QColor("#444444")))
            self.info_bg.setPen(QPen(QColor("#666666"), 2))

            if self.centrality < 0.25:
                # Level 1: Weak (Dark Grey)
                c_start = QColor("#666666")
                c_end = QColor("#444444")
                border = QColor("#333333")
                label_col = QColor("#CCCCCC")

                hover_start = QColor("#777777")
                hover_end = QColor("#555555")
                hover_border = QColor("#666666")

            elif self.centrality < 0.50:
                # Level 2: Medium (Light Grey)
                c_start = QColor("#AAAAAA")
                c_end = QColor("#888888")
                border = QColor("#666666")

                hover_start = QColor("#BBBBBB")
                hover_end = QColor("#999999")
                hover_border = QColor("#888888")

            elif self.centrality < 0.75:
                # Level 3: Bright Silver (Closer to white)
                c_start = QColor("#DDDDDD")
                c_end = QColor("#BBBBBB")
                border = QColor("#999999")

                hover_start = QColor("#EEEEEE")
                hover_end = QColor("#CCCCCC")
                hover_border = QColor("#AAAAAA")

            else:
                # Level 4: "Glow" (White body, Purple Border) - FIX: Body is Greyscale
                c_start = QColor("#FFFFFF")
                c_end = QColor("#F0F0F5")  # Almost white, tiny cool tint

                # THE GLOW: Use a bright purple border
                border = QColor("#A29BFE")

                hover_start = QColor("#FFFFFF")
                hover_end = QColor("#E0E0FF")
                hover_border = QColor("#6C5CE7")  # Stronger purple on hover

        # --- APPLY GRADIENTS ---
        self.normal_gradient = QRadialGradient(0, -5, self.normal_size / 2)
        self.normal_gradient.setColorAt(0, c_start)
        self.normal_gradient.setColorAt(1, c_end)

        self.hover_gradient = QRadialGradient(0, -8, (self.normal_size * 1.4) / 2)
        self.hover_gradient.setColorAt(0, hover_start)
        self.hover_gradient.setColorAt(1, hover_end)

        self.border_color = border
        self.hover_border_color = hover_border

        self.setBrush(QBrush(self.normal_gradient))
        self.setPen(QPen(self.border_color, 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.label.setDefaultTextColor(label_col)
        self.info_text.setDefaultTextColor(info_col)

    def update_tooltip_pos(self):
        text_rect = self.info_text.boundingRect()
        padding = 8
        bg_width = text_rect.width() + padding * 2
        bg_height = text_rect.height() + padding

        # Position relative to dynamic size so it doesn't overlap
        y_offset = -(self.normal_size / 2) - 35

        self.info_bg.setRect(-bg_width / 2, y_offset, bg_width, bg_height)
        self.info_text.setPos(-text_rect.width() / 2, y_offset + padding / 2)

    def animate_size(self, target_scale):
        # Calculate target rect based on SELF.NORMAL_SIZE (which is dynamic)
        # This ensures we scale relative to the influencer size, not 50px
        base = self.normal_size
        scaled = base * target_scale

        target_rect = QRectF(-scaled / 2, -scaled / 2, scaled, scaled)
        steps = 10
        for i in range(steps + 1):
            QTimer.singleShot(i * 15, lambda s=i / steps, tr=target_rect: self._update_size(s, tr))

    def _update_size(self, progress, target_rect):
        current_rect = self.rect()
        new_width = current_rect.width() + (target_rect.width() - current_rect.width()) * 0.3
        new_height = current_rect.height() + (target_rect.height() - current_rect.height()) * 0.3
        half_w = new_width / 2
        half_h = new_height / 2
        self.setRect(-half_w, -half_h, new_width, new_height)

    def hoverEnterEvent(self, event):
        self.is_hovered = True

        # Scale UP (1.3x of normal_size)
        self.animate_size(1.3)

        self.setBrush(QBrush(self.hover_gradient))
        self.setPen(QPen(self.hover_border_color, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setZValue(10)
        self.shadow.setBlurRadius(25)
        self.shadow.setOffset(0, 5)
        self.shadow.setColor(QColor(0, 0, 0, 160))

        # Show Floating Tooltip
        self.info_text.setVisible(True)
        self.info_bg.setVisible(True)

        for edge in self.outgoing_edges + self.incoming_edges:
            edge.highlight(True)

        # Show Info Panel (Bottom Corner)
        if self.graph_view:
            self.graph_view.show_node_details(self)

        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.is_hovered = False

        # Scale DOWN (Return to 1.0x of normal_size)
        self.animate_size(1.0)

        self.setBrush(QBrush(self.normal_gradient))
        self.setPen(QPen(self.border_color, 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setZValue(0)
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 3)
        self.shadow.setColor(QColor(0, 0, 0, 100))

        # Hide Floating Tooltip
        self.info_text.setVisible(False)
        self.info_bg.setVisible(False)

        for edge in self.outgoing_edges + self.incoming_edges:
            edge.highlight(False)

        # Hide Info Panel (Bottom Corner)
        if self.graph_view:
            self.graph_view.hide_node_details()

        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.outgoing_edges + self.incoming_edges:
                edge.update_position()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        # --- NEW: Path Finding Logic ---
        if self.graph_view and self.graph_view.path_mode:
            if self.graph_view.path_start_node is None:
                # First Click: Select Start Node
                self.graph_view.path_start_node = self
                self.graph_view.path_btn.setText("Click End Node")
                # Highlight this node Green to show selection
                self.setBrush(QBrush(QColor("#00B894")))
                return
            else:
                # Second Click: Select End Node & Calculate
                start = self.graph_view.path_start_node
                self.graph_view.visualize_path(start, self)
                return
        # -------------------------------

        # --- NEW: Recommendation Logic ---
        if self.graph_view and self.graph_view.rec_mode:
            self.graph_view.visualize_recommendations(self)
            return
        # ---------------------------------

        # --- AI Logic (Two-Step Selection) ---
        if self.graph_view and self.graph_view.ai_mode:

            # Step 1: Select First Node
            if self.graph_view.ai_start_node is None:
                self.graph_view.ai_start_node = self
                self.graph_view.ai_btn.setText("Click User 2")
                # Highlight Green
                self.setBrush(QBrush(QColor("#00CEC9")))
                return

            # Step 2: Select Second Node & Execute
            else:
                u1 = self.graph_view.ai_start_node
                u2 = self

                # Prevent clicking same node twice
                if u1 == u2: return

                self.graph_view.visualize_ai_predictions(u1, u2)
                return
        # -------------------------------------

        self.is_being_dragged = True
        self.velocity_x = 0
        self.velocity_y = 0
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_being_dragged = False
        super().mouseReleaseEvent(event)

    def fade_to(self, target_opacity, duration=300):
        """Smoothly animates opacity changes"""
        start_opacity = self.opacity()
        steps = 15  # Number of animation frames
        interval = duration // steps

        for i in range(steps + 1):
            t = i / steps
            # Linear interpolation
            new_op = start_opacity + (target_opacity - start_opacity) * t
            QTimer.singleShot(i * interval, lambda val=new_op: self.setOpacity(val))


# ---------- NETWORK GRAPH PAGE ----------
class NetworkGraph(QGraphicsView):
    def __init__(self, matrix=None, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.matrix = matrix if matrix is not None else []

        # Initialize Audio
        self.audio_manager = AudioManager()

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-400, -400, 800, 800)
        self.setScene(self.scene)

        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        self.matrix = matrix
        self.nodes = []
        self.initial_positions = []
        self.final_positions = []

        self.physics_enabled = True
        self.physics_timer = QTimer()
        self.physics_timer.timeout.connect(self.apply_physics)
        self.physics_timer.start(16)

        self.setup_graph()
        self.setup_info_panel()
        self.update_theme()

        self.path_mode = False
        self.path_start_node = None

        # --- NEW: Recommendation Mode State ---
        self.rec_mode = False
        self.temp_rec_items = []  # Store dashed lines to delete later
        # --------------------------------------

        self.reset_timer = QTimer(self)
        self.reset_timer.setSingleShot(True)  # Runs once then stops
        self.reset_timer.timeout.connect(self.clear_recommendations)


        if self.main_window:
            self.back_btn = QPushButton("⬅  Back", self)
            self.back_btn.setFixedSize(100, 36)
            self.back_btn.move(15, 15)
            self.back_btn.clicked.connect(self.audio_manager.play_click)
            self.back_btn.clicked.connect(self.go_back)
            self.back_btn.raise_()
            self.back_btn.setCursor(Qt.PointingHandCursor)

            # --- NEW: Find Path Button ---
            self.path_btn = QPushButton("🔍 Find Path", self)
            self.path_btn.setFixedSize(140, 36)
            self.path_btn.move(130, 15)  # Positioned next to Back button
            self.path_btn.clicked.connect(self.audio_manager.play_click)
            self.path_btn.clicked.connect(self.toggle_path_mode)
            self.path_btn.raise_()
            self.path_btn.setCursor(Qt.PointingHandCursor)

            # Style the button
            self.path_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #6C5CE7; color: white; border-radius: 8px; font-weight: bold;
                            }
                            QPushButton:hover { background-color: #A29BFE; }
                            QPushButton:checked { background-color: #FD79A8; border: 2px solid white; }
                        """)
            self.path_btn.setCheckable(True)
            # -----------------------------

            # --- NEW: Recommendation Button ---
            self.rec_btn = QPushButton("★ Suggestions", self)
            self.rec_btn.setFixedSize(140, 36)
            self.rec_btn.move(280, 15)  # Positioned to the right of Path button
            self.rec_btn.clicked.connect(self.audio_manager.play_click)
            self.rec_btn.clicked.connect(self.toggle_rec_mode)
            self.rec_btn.raise_()
            self.rec_btn.setCursor(Qt.PointingHandCursor)

            # --- NEW PURPLE THEME ---
            self.rec_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #6C5CE7; color: white; border-radius: 8px; font-weight: bold;
                            }
                            QPushButton:hover { background-color: #A29BFE; }
                            QPushButton:checked { background-color: #FD79A8; border: 2px solid white; }
                        """)
            self.rec_btn.setCheckable(True)
            # ----------------------------------

            # --- NEW: AI Prediction Button ---
            self.ai_btn = QPushButton("🔮 AI Predict", self)
            self.ai_btn.setFixedSize(140, 36)
            self.ai_btn.move(430, 15)  # Moved to the right of Suggestions button
            self.ai_btn.clicked.connect(self.audio_manager.play_click)
            self.ai_btn.clicked.connect(self.toggle_ai_mode)
            self.ai_btn.raise_()
            self.ai_btn.setCursor(Qt.PointingHandCursor)

            # Cyan Theme for AI
            self.ai_btn.setStyleSheet("""
                                    QPushButton {
                                        background-color: #6C5CE7; color: white; border-radius: 8px; font-weight: bold;
                                    }
                                    QPushButton:hover { background-color: #00CEC9; }
                                    QPushButton:checked { background-color: #00CEC9; border: 2px solid white; }
                                """)
            self.ai_btn.setCheckable(True)

            # Add AI state
            self.ai_mode = False

            # --- NEW: Path Result Label (Hidden by default) ---
            self.lbl_path_result = QLabel("", self)
            self.lbl_path_result.setStyleSheet("""
                        background-color: rgba(40, 40, 40, 220); 
                        color: #FFD700; 
                        border: 1px solid #FFD700;
                        border-radius: 10px;
                        padding: 8px 15px;
                        font-family: Arial;
                        font-size: 13px;
                        font-weight: bold;
                    """)
            self.lbl_path_result.hide()
            # --------------------------------------------------

            def resizeEvent(self, event):
                super().resizeEvent(event)
                # Keep path label at bottom left
                if hasattr(self, 'lbl_path_result'):
                    self.lbl_path_result.move(20, self.height() - 60)
                # (Keep your existing info_panel update logic here too if you have it)

    def setup_info_panel(self):
        self.info_panel = QFrame(self)
        self.info_panel.setFixedWidth(260)
        self.info_panel.setVisible(False)

        self.info_panel.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(15, 15, 15, 15)

        self.lbl_title = QLabel("User Details")
        self.lbl_title.setObjectName("Title")

        self.lbl_id = QLabel("ID: -")
        self.lbl_user = QLabel("Username: -")
        self.lbl_followers = QLabel("Followers: -")
        self.lbl_following = QLabel("Following: -")
        self.lbl_interests = QLabel("Interests: -")
        self.lbl_interests.setWordWrap(True)

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_id)
        layout.addWidget(self.lbl_user)
        layout.addWidget(self.lbl_followers)
        layout.addWidget(self.lbl_following)
        layout.addWidget(self.lbl_interests)

        self.info_panel.setLayout(layout)

    def show_node_details(self, node):
        followers = len(node.incoming_edges)
        following = len(node.outgoing_edges)
        if node.interests:
            interests_str = ", ".join(node.interests)
        else:
            interests_str = "None"

        self.lbl_id.setText(f"<b>ID:</b> {node.id}")
        self.lbl_user.setText(f"<b>Username:</b> {node.username}")
        self.lbl_followers.setText(f"<b>Followers:</b> {followers}")
        self.lbl_following.setText(f"<b>Following:</b> {following}")
        self.lbl_interests.setText(f"<b>Interests:</b> {interests_str}")

        self.info_panel.setVisible(True)
        self.info_panel.raise_()
        self.update_panel_position()

    def hide_node_details(self):
        self.info_panel.setVisible(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_panel_position()

    def update_panel_position(self):
        if hasattr(self, 'info_panel') and self.info_panel.isVisible():
            self.info_panel.adjustSize()
            margin = 20
            w = self.info_panel.width()
            h = self.info_panel.height()
            x = self.width() - w - margin
            y = self.height() - h - margin
            self.info_panel.move(x, y)

    def update_theme(self):
        # 1. Handle Node Colors
        is_dark = False
        if self.main_window and hasattr(self.main_window, 'dark_mode'):
            is_dark = self.main_window.dark_mode

        if is_dark:
            self.setBackgroundBrush(QBrush(QColor("#2C2C2C")))
            if hasattr(self, 'info_panel'):
                self.info_panel.setStyleSheet("""
                    QFrame { background-color: rgba(50, 50, 50, 230); border: 2px solid #888; border-radius: 12px; padding: 10px; }
                    QLabel { background: transparent; border: none; color: #EDEDED; font-size: 13px; }
                    QLabel#Title { font-weight: bold; font-size: 16px; color: #A29BFE; padding-bottom: 5px; border-bottom: 1px solid #666; }
                """)
        else:
            self.setBackgroundBrush(QBrush(QColor("#F8F9FD")))
            if hasattr(self, 'info_panel'):
                self.info_panel.setStyleSheet("""
                    QFrame { background-color: rgba(255, 255, 255, 230); border: 2px solid #6C5CE7; border-radius: 12px; padding: 10px; }
                    QLabel { background: transparent; border: none; color: #2D3436; font-size: 13px; }
                    QLabel#Title { font-weight: bold; font-size: 16px; color: #6C5CE7; padding-bottom: 5px; border-bottom: 1px solid #ddd; }
                """)

        for node in self.nodes:
            node.update_theme()
            for edge in node.outgoing_edges:
                edge.update_theme()

        # 2. Handle Button Styles (THE FIX)
        if is_dark:
            # DARK MODE: Gray -> Lighter Gray -> Cyan (Active)
            btn_style = """
                QPushButton {
                    background-color: #636e72; color: white; border-radius: 8px; font-weight: bold;
                }
                QPushButton:hover { background-color: #b2bec3; color: #2d3436; }
                QPushButton:checked { background-color: #00CEC9; border: 2px solid white; color: #2d3436; }
            """
        else:
            # LIGHT MODE: Purple -> Lighter Purple -> Pink (Active)
            btn_style = """
                QPushButton {
                    background-color: #6C5CE7; color: white; border-radius: 8px; font-weight: bold;
                }
                QPushButton:hover { background-color: #A29BFE; }
                QPushButton:checked { background-color: #FD79A8; border: 2px solid white; }
            """

        # Apply to buttons ONLY if they are NOT currently active/checked
        if hasattr(self, 'path_btn') and not self.path_btn.isChecked():
            self.path_btn.setStyleSheet(btn_style)

        if hasattr(self, 'rec_btn') and not self.rec_btn.isChecked():
            self.rec_btn.setStyleSheet(btn_style)

        if hasattr(self, 'ai_btn') and not self.ai_btn.isChecked():
            self.ai_btn.setStyleSheet(btn_style)

    def go_back(self):
        if self.main_window:
            self.main_window.go_to_login()

    def apply_physics(self):
        if not self.physics_enabled:
            return

        damping = 0.85
        spring_strength = 0.01  # Increased slightly for snappier edges
        ideal_distance = 150
        repulsion_strength = 10000
        collision_radius = 60  # Increased to prevent big nodes overlapping

        # Base gravity for everyone (keeps nodes from flying off into space)
        base_gravity = 0.002

        for node in self.nodes:
            if node.is_being_dragged or node.is_hovered:
                continue

            force_x = 0
            force_y = 0

            # 1. Repulsion (Nodes push each other away)
            for other in self.nodes:
                if other == node: continue
                dx = node.pos().x() - other.pos().x()
                dy = node.pos().y() - other.pos().y()
                distance = math.sqrt(dx * dx + dy * dy)

                if distance > 600: continue  # Optimization

                if distance < 0.1: distance = 0.1
                repulsion = repulsion_strength / (distance * distance)
                force_x += (dx / distance) * repulsion
                force_y += (dy / distance) * repulsion

            # 2. Springs (Connections pull nodes together)
            for edge in node.outgoing_edges + node.incoming_edges:
                other = edge.dest if edge.source == node else edge.source
                dx = other.pos().x() - node.pos().x()
                dy = other.pos().y() - node.pos().y()
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < 0.1: distance = 0.1
                spring_force = (distance - ideal_distance) * spring_strength
                force_x += (dx / distance) * spring_force
                force_y += (dy / distance) * spring_force

            # 3. Collision (Prevent Overlap)
            for other in self.nodes:
                if other == node: continue
                dx = node.pos().x() - other.pos().x()
                dy = node.pos().y() - other.pos().y()
                distance = math.sqrt(dx * dx + dy * dy)

                # Use dynamic sizes for collision calculation
                # (Assuming node.normal_size is available from our previous Node class update)
                combined_radius = (node.normal_size / 2) + (other.normal_size / 2) + 10

                if distance < combined_radius:
                    if distance < 0.1: distance = 0.1
                    collision_force = (combined_radius - distance) * 0.5
                    force_x += (dx / distance) * collision_force
                    force_y += (dy / distance) * collision_force

            # 4. VARIABLE CENTRAL GRAVITY (The Logic You Wanted)
            # - Weak nodes (0.0 score) get 0.002 gravity (Base)
            # - Strong nodes (1.0 score) get 0.032 gravity (16x stronger pull!)
            centrality_pull = node.centrality * 0.005
            total_gravity = base_gravity + centrality_pull

            force_x -= node.x() * total_gravity
            force_y -= node.y() * total_gravity

            # Apply forces
            node.velocity_x = (node.velocity_x + force_x) * damping
            node.velocity_y = (node.velocity_y + force_y) * damping

            # Stop micro-movements (jitter fix)
            if abs(node.velocity_x) < 0.05: node.velocity_x = 0
            if abs(node.velocity_y) < 0.05: node.velocity_y = 0

            if abs(node.velocity_x) > 0 or abs(node.velocity_y) > 0:
                node.setPos(node.pos() + QPointF(node.velocity_x, node.velocity_y))

    def setup_graph(self):
        self.scene.clear()
        self.nodes = []

        # 1. Get Graph Data
        if self.matrix:
            matrix = self.matrix
        elif self.main_window:
            matrix = self.main_window.app.network.graph
        else:
            return

        num_nodes = len(matrix)
        if num_nodes == 0: return

        ## 2. Calculate Influence
        scores = {}
        if self.main_window:
            try:
                scores = self.main_window.app.network.calculate_influence()
            except AttributeError:
                scores = {i: 0.0 for i in range(num_nodes)}

        # 3. Create Nodes
        # Layout Logic: 1 Node = Center, >1 Nodes = Circle
        radius = 0 if num_nodes == 1 else 300

        for i in range(num_nodes):
            angle = 2 * math.pi * i / max(1, num_nodes)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            # Get the score for this user
            user_score = scores.get(i, 0.0)

            # --- THE CRITICAL FIX ---
            # We call Node() with the EXACT arguments from your class definition:
            # def __init__(self, node_id, x, y, main_window, graph_view, audio_manager, centrality)
            node = Node(
                node_id=i,
                x=x,
                y=y,
                main_window=self.main_window,
                graph_view=self,
                audio_manager=self.audio_manager,
                centrality=user_score
            )
            # ------------------------

            if node.is_valid:
                self.scene.addItem(node)
                self.nodes.append(node)
                node.setPos(x, y)

        # 4. Create Edges
        for i in range(num_nodes):
            for j in range(num_nodes):
                if matrix[i][j] == 1:
                    n1 = next((n for n in self.nodes if n.id == i), None)
                    n2 = next((n for n in self.nodes if n.id == j), None)

                    if n1 and n2:
                        edge = DirectedEdge(n1, n2)
                        self.scene.addItem(edge)
                        n1.outgoing_edges.append(edge)
                        n2.incoming_edges.append(edge)

        # 5. Reset Z-Values so nodes stay above edges
        for node in self.nodes:
            node.setZValue(0)

    def animate_nodes(self):
        if self.animation_step >= self.total_steps:
            self.timer.stop()
            return
        t = (self.animation_step + 1) / self.total_steps
        if t < 1: t = 1 - math.pow(1 - t, 3)
        for node, start, end in zip(self.nodes, self.initial_positions, self.final_positions):
            node.setPos(start.x() * (1 - t) + end.x() * t, start.y() * (1 - t) + end.y() * t)
            if self.animation_step < 20:
                node.setOpacity(self.animation_step / 20)
        self.animation_step += 1

    def wheelEvent(self, event):
        zoom = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom, zoom)
        else:
            self.scale(1 / zoom, 1 / zoom)

    def toggle_path_mode(self):
        self.path_mode = self.path_btn.isChecked()
        self.path_start_node = None
        self.reset_path_visuals()

        if self.path_mode:
            self.path_btn.setText("Click Start Node")
            # Active: Pink
            self.path_btn.setStyleSheet(
                "background-color: #FD79A8; color: white; border-radius: 8px; font-weight: bold;")
        else:
            self.path_btn.setText("🔍 Find Path")
            self.update_theme()

    def reset_path_visuals(self):
        # 1. Hide the result label
        if hasattr(self, 'lbl_path_result'):
            self.lbl_path_result.hide()

        # 2. Reset Nodes
        for node in self.nodes:
            node.fade_to(1.0)
            node.update_theme()
            # Ensure nodes are back at standard level (0)
            # (unless hovered, but this resets the baseline)
            if not node.is_hovered:
                node.setZValue(0)

        # 3. Reset Edges
        for node in self.nodes:
            for edge in node.outgoing_edges:
                edge.fade_to(0.7)

                # --- THE FIX ---
                # Force the edge back to the background layer
                edge.setZValue(-1)
                # ---------------

                edge.update_theme()

    def reset_path_ui(self):
        """Resets the Path Button text and color after animation ends"""
        self.path_btn.setText("🔍 Find Path")
        self.update_theme()
        self.reset_path_visuals()

    def visualize_path(self, start_node, end_node):
        if not self.main_window: return

        path_ids = self.main_window.app.network.get_shortest_path(start_node.id, end_node.id)

        if not path_ids:
            self.path_btn.setText("No Path Found!")
            self.audio_manager.play_error()
            QTimer.singleShot(2000, lambda: self.path_btn.setText("Click Start Node"))
            return

        # 1. Dim Everything Smoothly EXCEPT the Start Node
        for item in self.scene.items():
            if isinstance(item, (Node, DirectedEdge)):
                # --- THE FIX: Skip the Start Node so it stays visible ---
                if item == start_node:
                    item.setOpacity(1.0)  # Force full visibility just in case
                    item.setZValue(10) # Force Start Node above the coming edge (which is Z=5)
                    continue
                    # --------------------------------------------------------

                item.fade_to(0.15)

                # 2. Setup Animation
        self.current_path_ids = path_ids
        self.path_step_index = 0

        # Construct path string
        names = []
        for uid in path_ids:
            node = next((n for n in self.nodes if n.id == uid), None)
            names.append(node.username if node else f"User {uid}")
        self.final_path_str = "Path: " + " ➜ ".join(names)

        self.path_btn.setText("Tracing...")

        # Start the edge animation loop
        QTimer.singleShot(500, self.animate_next_edge)

    def animate_next_edge(self):
        # Check if we reached the end
        if self.path_step_index >= len(self.current_path_ids) - 1:
            self.path_btn.setText("Path Found!")
            self.path_mode = False
            self.path_btn.setChecked(False)

            # --- DYNAMIC LABEL COLOR ---
            # Check mode to set the correct label text color
            is_dark = self.main_window.dark_mode if self.main_window else False
            if is_dark:
                res_color = "#FFD700"  # Gold for Dark Mode
                bg_color = "rgba(40, 40, 40, 220)"
            else:
                res_color = "#00b894"  # Green for Light Mode
                bg_color = "rgba(255, 255, 255, 220)"

            self.lbl_path_result.setText(self.final_path_str)
            self.lbl_path_result.setStyleSheet(f"""
                background-color: {bg_color}; 
                color: {res_color}; 
                border: 2px solid {res_color};
                border-radius: 10px;
                padding: 8px 15px;
                font-family: Arial;
                font-size: 13px;
                font-weight: bold;
            """)
            self.lbl_path_result.adjustSize()
            self.lbl_path_result.move(20, self.height() - self.lbl_path_result.height() - 20)

            # Show with fade effect
            effect = QGraphicsOpacityEffect(self.lbl_path_result)
            self.lbl_path_result.setGraphicsEffect(effect)
            self.lbl_path_result.show()

            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(500)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start()
            self.active_anim = anim

            QTimer.singleShot(5000, self.reset_path_ui)
            return

        # Get Current Step
        u1 = self.current_path_ids[self.path_step_index]
        u2 = self.current_path_ids[self.path_step_index + 1]

        n1 = next((n for n in self.nodes if n.id == u1), None)
        n2 = next((n for n in self.nodes if n.id == u2), None)

        if n1 and n2:
            # --- COLOR SELECTION LOGIC ---
            is_dark = self.main_window.dark_mode if self.main_window else False

            if is_dark:
                # DARK MODE: Original Gold
                path_color = QColor("#FFD700")
            else:
                # LIGHT MODE: New Emerald Green
                path_color = QColor("#00b894")

            path_pen = QPen(path_color, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            # -----------------------------

            # Animate Edge
            for edge in n1.outgoing_edges:
                if edge.dest.id == u2:
                    edge.setPen(path_pen)
                    edge.line.setPen(path_pen)
                    edge.setBrush(QBrush(path_color))
                    edge.setZValue(5)
                    edge.fade_to(1.0)
                    break

            # Animate Destination Node
            n2.setZValue(10)
            n2.fade_to(1.0)

            self.audio_manager.play_hover()

        self.path_step_index += 1
        QTimer.singleShot(700, self.animate_next_edge)

    def toggle_rec_mode(self):
        self.rec_mode = self.rec_btn.isChecked()
        self.clear_recommendations()  # Clear any existing lines

        # Turn off Path Mode if it's on (avoid conflict)
        if self.path_mode:
            self.path_btn.setChecked(False)
            self.toggle_path_mode()

        if self.rec_mode:
            self.rec_btn.setText("Click a User")
            # Active State: Pink (#FD79A8)
            self.rec_btn.setStyleSheet(
                "background-color: #FD79A8; color: white; border: 2px solid white; border-radius: 8px; font-weight: bold;")
        else:
            self.rec_btn.setText("★ Suggestions")
            self.update_theme()

    def clear_recommendations(self):
        # 1. Delete lines
        for item in self.temp_rec_items:
            self.scene.removeItem(item)
        self.temp_rec_items.clear()

        # 2. Reset Text
        self.rec_btn.setText("★ Suggestions")

        self.update_theme()
        # -----------------------------------------

        # 3. Reset Visuals
        self.reset_path_visuals()

    def visualize_recommendations(self, user_node):
        if not self.main_window: return

        # 1. STOP any pending reset (Fixes the glitch!)
        self.reset_timer.stop()

        # 2. Clear old lines immediately
        for item in self.temp_rec_items:
            self.scene.removeItem(item)
        self.temp_rec_items.clear()

        # 3. Get Recommendations
        recs = self.main_window.app.network.get_recommendations(user_node.id)

        if not recs:
            self.rec_btn.setText("No Matches!")
            self.audio_manager.play_error()
            self.reset_timer.start(2000)  # Reset in 2s
            return

        recommended_ids = [r[0] for r in recs]

        # 4. Apply Visuals (Force Opacity for targets to prevent conflicts)
        for item in self.scene.items():
            if isinstance(item, (Node, DirectedEdge)):

                # Case A: Important Nodes (Source or Recommended)
                if item == user_node or (isinstance(item, Node) and item.id in recommended_ids):
                    # FORCE Instant visibility (No animation)
                    item.setOpacity(1.0)
                    item.setZValue(10)
                    continue

                # Case B: Everyone else
                # Only animate if it's not already faded
                if item.opacity() > 0.15:
                    item.fade_to(0.1)
                item.setZValue(0)

        # 5. Draw Lines & Labels
        for rec_id, score in recs:
            target_node = next((n for n in self.nodes if n.id == rec_id), None)
            if target_node:
                # Line -> Change to PINK (#FD79A8)
                line = QGraphicsLineItem(user_node.x(), user_node.y(), target_node.x(), target_node.y())
                line.setPen(QPen(QColor("#FD79A8"), 3, Qt.DashLine))
                line.setZValue(-2)
                self.scene.addItem(line)
                self.temp_rec_items.append(line)

                # Label -> Change to PINK (#FD79A8)
                mid_x = (user_node.x() + target_node.x()) / 2
                mid_y = (user_node.y() + target_node.y()) / 2
                lbl = QGraphicsTextItem(f"{int(score * 100)}%")
                lbl.setFont(QFont("Arial", 10, QFont.Bold))
                lbl.setDefaultTextColor(QColor("#FD79A8"))
                lbl.setPos(mid_x, mid_y)
                lbl.setZValue(50)
                self.scene.addItem(lbl)
                self.temp_rec_items.append(lbl)

        self.rec_btn.setText("Matches Found!")
        self.rec_mode = False
        self.rec_btn.setChecked(False)

        # 6. Restart the 5-second timer
        self.reset_timer.start(5000)

    def refresh_graph(self):
        """Reload the graph data from the backend"""
        if self.main_window:
            # 1. Clear current items
            self.scene.clear()
            # 2. Fetch latest matrix from social_network.py
            self.matrix = self.main_window.app.network.get_graph()
            # 2. Debug Print (Optional: Check your console to see if data exists!)
            print(f"DEBUG: Refreshing Graph. Matrix size: {len(self.matrix)}")
            # 3. Re-run setup
            self.setup_graph()

    def showEvent(self, event):
        """
        Triggered automatically whenever this page becomes visible.
        We use this to refresh the data from the DB so the graph is always up-to-date.
        """
        # 1. Call the parent implementation (Important for Qt internals)
        super().showEvent(event)

        # 2. Refresh the graph
        print("DEBUG: NetworkGraph page opened, refreshing data...")
        self.refresh_graph()

    def toggle_ai_mode(self):
        self.ai_mode = self.ai_btn.isChecked()
        self.clear_recommendations()

        # Reset the selection state
        self.ai_start_node = None

        if self.path_mode: self.path_btn.setChecked(False); self.toggle_path_mode()
        if self.rec_mode: self.rec_btn.setChecked(False); self.toggle_rec_mode()

        if self.ai_mode:
            # Force retrain to be safe
            if self.main_window:
                self.main_window.app.predictor.train_model()

            self.ai_btn.setText("Click User 1")
            self.ai_btn.setStyleSheet(
                "background-color: #00CEC9; color: white; border: 2px solid white; border-radius: 8px; font-weight: bold;")
        else:
            self.ai_btn.setText("🔮 AI Predict")
            self.update_theme()

    def visualize_ai_predictions(self, u1_node, u2_node):
        if not self.main_window: return

        # 1. Get Prediction
        # predictor.predict_pair returns tuple: (result, features)
        result, features = self.main_window.app.predictor.predict_follow(u1_node.id, u2_node.id)

        # 2. Draw Visuals
        self.temp_rec_items.clear()

        # Choose color: Cyan for Match, Gray for No Match
        color = "#00CEC9" if result == 1 else "#B2BEC3"
        text = "AI: MATCH!" if result == 1 else "AI: No Match"

        # Draw Line
        line = QGraphicsLineItem(u1_node.x(), u1_node.y(), u2_node.x(), u2_node.y())
        line.setPen(QPen(QColor(color), 4, Qt.DashLine))
        line.setZValue(10)
        self.scene.addItem(line)
        self.temp_rec_items.append(line)

        # Draw Label
        mid_x = (u1_node.x() + u2_node.x()) / 2
        mid_y = (u1_node.y() + u2_node.y()) / 2
        lbl = QGraphicsTextItem(text)
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        lbl.setDefaultTextColor(QColor(color))
        lbl.setPos(mid_x, mid_y)
        lbl.setZValue(50)

        # Add background to text so it's readable
        bg = QGraphicsRectItem(lbl.boundingRect())
        bg.setBrush(QBrush(QColor(0, 0, 0, 180)))
        bg.setPos(mid_x, mid_y)
        bg.setZValue(49)
        self.scene.addItem(bg)
        self.temp_rec_items.append(bg)
        self.scene.addItem(lbl)

        self.temp_rec_items.append(lbl)

        # 3. Reset UI
        self.ai_btn.setText("Result Shown")
        self.ai_mode = False
        self.ai_btn.setChecked(False)
        self.ai_start_node = None
        self.update_theme()

        # 4. LAUNCH 3D PLOT (This opens the cool window!)
        self.main_window.app.predictor.visualize_prediction_3d(u1_node.id, u2_node.id)

        # Auto-clear line after 5 seconds
        self.reset_timer.start(5000)