from PyQt5 import QtWidgets,QtGui,QtCore,Qt
from PyQt5.QtMultimedia import QMediaContent,QMediaPlayer
import qtawesome as qta
import requests,traceback


font=QtGui.QFont()
song_font = QtGui.QFont()
font.setFamily("STXihei")
font.setPointSize(20)
song_font.setFamily("STXihei")
song_font.setPointSize(14)


class ToggleButton():
    checkedChanged = QtCore.pyqtSignal(bool)
    def __init__(self,parent=None):
        super(QtWidgets.QWidget, self).__init__(parent)

        self.checked = False
        self.bgColorOff = QtGui.QColor(255, 255, 255)
        self.bgColorOn = QtGui.QColor(0, 0, 0)

        self.sliderColorOff = QtGui.QColor(100, 100, 100)
        self.sliderColorOn = QtGui.QColor(100, 184, 255)

        self.textColorOff = QtGui.QColor(143, 143, 143)
        self.textColorOn = QtGui.QColor(255, 255, 255)

        self.textOff = "OFF"
        self.textOn = "ON"

        self.space = 2
        self.rectRadius = 5

        self.step = self.width() / 50
        self.startX = 0
        self.endX = 0

        self.timer = QtCore.QTimer(self)  # 初始化一个定时器
        self.timer.timeout.connect(self.updateValue)  # 计时结束调用operate()方法

        #self.timer.start(5)  # 设置计时间隔并启动

        self.setFont(QtGui.QFont("Microsoft Yahei", 10))

        #self.resize(55,22)

    def updateValue(self):
        if self.checked:
            if self.startX < self.endX:
                self.startX = self.startX + self.step
            else:
                self.startX = self.endX
                self.timer.stop()
        else:
            if self.startX  > self.endX:
                self.startX = self.startX - self.step
            else:
                self.startX = self.endX
                self.timer.stop()

        self.update()


    def mousePressEvent(self,event):
        self.checked = not self.checked
        #发射信号
        self.checkedChanged.emit(self.checked)

        # 每次移动的步长为宽度的50分之一
        self.step = self.width() / 50
        #状态切换改变后自动计算终点坐标
        if self.checked:
            self.endX = self.width() - self.height()
        else:
            self.endX = 0
        self.timer.start(5)

    def paintEvent(self, evt):
        #绘制准备工作, 启用反锯齿
            painter = QtGui.QPainter()



            painter.begin(self)

            painter.setRenderHint(QtGui.QPainter.Antialiasing)


            #绘制背景
            self.drawBg(evt, painter)
            #绘制滑块
            self.drawSlider(evt, painter)
            #绘制文字
            self.drawText(evt, painter)

            painter.end()


    def drawText(self, event, painter):
        painter.save()

        if self.checked:
            painter.setPen(self.textColorOn)
            painter.drawText(0, 0, self.width() / 2 + self.space * 2, self.height(), Qt.AlignCenter, self.textOn)
        else:
            painter.setPen(self.textColorOff)
            painter.drawText(self.width() / 2, 0,self.width() / 2 - self.space, self.height(), Qt.AlignCenter, self.textOff)

        painter.restore()


    def drawBg(self, event, painter):
        painter.save()
        painter.setPen(Qt.NoPen)

        if self.checked:
            painter.setBrush(self.bgColorOn)
        else:
            painter.setBrush(self.bgColorOff)

        rect = QtCore.QRect(0, 0, self.width(), self.height())
        #半径为高度的一半
        radius = rect.height() / 2
        #圆的宽度为高度
        circleWidth = rect.height()

        path = QtGui.QPainterPath()
        path.moveTo(radius, rect.left())
        path.arcTo(QtCore.QRectF(rect.left(), rect.top(), circleWidth, circleWidth), 90, 180)
        path.lineTo(rect.width() - radius, rect.height())
        path.arcTo(QtCore.QRectF(rect.width() - rect.height(), rect.top(), circleWidth, circleWidth), 270, 180)
        path.lineTo(radius, rect.top())

        painter.drawPath(path)
        painter.restore()

    def drawSlider(self, event, painter):
        painter.save()

        if self.checked:
            painter.setBrush(self.sliderColorOn)
        else:
            painter.setBrush(self.sliderColorOff)

        rect = QtCore.QRect(0, 0, self.width(), self.height())
        sliderWidth = rect.height() - self.space * 2
        sliderRect = QtCore.QRect(self.startX + self.space, self.space, sliderWidth, sliderWidth)
        painter.drawEllipse(sliderRect)

        painter.restore()

class Music(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.var_song_name = ''
        self.setFixedSize(400,200)
        self.setWindowTitle("🎧+📚=😊")
        self.setWindowOpacity(0.8)

        self.init_ui()
        self.custom_style()
        self.mode = 'False'         # 初始UI设置为光亮模式
        self.play_status = False    # 播放状态初始化为否
        self.player = QMediaPlayer(self)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.check_music_status)

    def getState(self,checked):
        print("checked=", checked)

    # 设置样式
    def custom_style(self):
        self.setStyleSheet('''
            #main_widget{
                border-radius:5px;
                background:white;
            }
            #play_btn,#pervious_btn,#next_btn{
                border:none;
            }
            #play_btn:hover,#pervious_btn:hover,#next_btn:hover{
                background:	#696969;
                border-radius:5px;
                
            }
        ''')
        self.close_btn.setStyleSheet('''
            QPushButton{
                background:#F76677;
                border-radius:5px;
                }
            QPushButton:hover{
                background:red;
                }''')
        self.status_label.setStyleSheet('''
            QLabel{
                background:#FFD85A;
                border-radius:5px;
                }
        ''')

    def init_ui(self):
        # 窗口布局

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setObjectName("main_widget")
        self.main_layout = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        # 标题
        self.title_lable = QtWidgets.QLabel('🌥WindPlayer')
        self.title_lable.setFont(font)
        self.title_lable.setStyleSheet('''
        QLabel{
                color:"black";
                }
        ''')

        # Toggle Button
        self.switchBtn = ToggleButton(self)
        self.switchBtn.checkedChanged.connect(self.switch_mode)
        self.title_lable.setFont(font)
        self.title_lable.setAlignment(QtCore.Qt.AlignCenter)

        # 关闭按钮
        self.close_btn = QtWidgets.QPushButton("")  # 关闭按钮
        self.close_btn.clicked.connect(self.close_btn_event)
        self.close_btn.setFixedSize(15,15)

        # 音乐状态按钮
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setFixedSize(15,15)

        # 播放按钮
        play_icon = qta.icon("fa.play-circle-o",)
        self.play_btn = QtWidgets.QPushButton(play_icon,"")
        self.play_btn.setIconSize(QtCore.QSize(50, 50))
        self.play_btn.setFixedSize(82,82)
        self.play_btn.setObjectName("play_btn")
        self.play_btn.clicked.connect(self.play_music)
        self.play_btn.setStyleSheet('''
                    QPushButton{
                        background:white;
                        border-radius:5px;
                        }
                    QPushButton:hover{
                        background:	#e9e9e9;
                        }''')


        # 下一首按钮
        next_icon = qta.icon("fa.chevron-right")
        self.next_btn = QtWidgets.QPushButton(next_icon,"")
        self.next_btn.setIconSize(QtCore.QSize(50,50))
        self.next_btn.setFixedSize(82,82)
        self.next_btn.setObjectName("next_btn")
        self.next_btn.clicked.connect(self.next_music)
        self.next_btn.setStyleSheet('''
            QPushButton{
                background:white;
                border-radius:5px;
                }
            QPushButton:hover{
                background:	#e9e9e9;
                }''')

        # 进度条
        self.process_bar = QtWidgets.QProgressBar()
        self.process_value = 0
        self.process_bar.setValue(self.process_value)
        self.process_bar.setFixedHeight(5)
        self.process_bar.setTextVisible(False)
        self.process_bar.setStyleSheet('''QProgressBar {   border: 2px solid grey;   border-radius: 5px;   background-color: #FFFFFF;}QProgressBar::chunk {   background-color: #05B8CC;   width: 28px;}QProgressBar {   border: 2px solid grey;   border-radius: 5px;   text-align: center;}
        ''')

        # 播放信息
        self.song_name = QtWidgets.QLabel('Nothing Playing')
        self.song_name.setFont(song_font)


        self.main_layout.addWidget(self.close_btn,0,0,1,1)
        self.main_layout.addWidget(self.title_lable,0,1,1,1)
        self.main_layout.addWidget(self.status_label,1,0,1,1)
        self.main_layout.addWidget(self.play_btn, 1, 1, 1, 1)
        self.main_layout.addWidget(self.next_btn, 1, 2, 1, 1)
        self.main_layout.addWidget(self.process_bar,2,0,1,3)
        self.main_layout.addWidget(self.song_name,3,0,1,3)
        self.setCentralWidget(self.main_widget)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框

    # 关闭程序
    def close_btn_event(self):
        self.close()
    # 夜间模式切换 （未完成 ）
    def switch_mode(self, checked):
        if checked:
            self.main_widget.setStyleSheet('''
            QWidget{
            "background-color: black"}
            ''')
        else:
            self.main_widget.setStyleSheet('''
            QWidget{
            "background-color: white"}
            ''')
    # 鼠标长按事件
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))

    # 鼠标移动事件
    def mouseMoveEvent(self, QMouseEvent):
        if QtCore.Qt.LeftButton and self.m_drag:
            self.move(QMouseEvent.globalPos() - self.m_DragPosition)
            QMouseEvent.accept()

    # 鼠标释放事件
    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    # 播放音乐
    def play_music(self):
        try:
            # 播放音乐
            if self.play_status is False:
                self.play_status = True # 设置播放状态为是
                self.play_btn.setIcon(qta.icon("fa.pause-circle-o")) # 设置播放图标
                player_status = self.player.mediaStatus() # 获取播放器状态
                # print("当前播放状态：",player_status)
                if player_status == 6:
                    # 设置状态标签为绿色
                    self.status_label.setStyleSheet('''QLabel{background:#72EA72;border-radius:5px;}''')
                    self.player.play()
                    self.song_name.setText(f'{self.var_song_name} - Playing')
                else:
                    self.next_music()
                    self.song_name.setText(f'{self.var_song_name} - Playing')
            # 暂停音乐
            else:
                # 设置状态为蓝色
                self.status_label.setStyleSheet('''QLabel{background:#0099CC;border-radius:5px;}''')
                self.play_status = False
                self.play_btn.setIcon(qta.icon("fa.play-circle-o"))
                self.player.pause()
                self.song_name.setText(f'{self.var_song_name} - Paused')
        except Exception as e:
            pass

    # 下一首音乐
    def next_music(self):
        try:
            # 设置状态为黄色
            self.status_label.setStyleSheet('''
                QLabel{
                    background:#FFBF00;
                    border-radius:5px;
                    }
            ''')
            self.play_status = True # 设置播放状态为是
            self.play_btn.setIcon(qta.icon("fa.pause-circle-o")) # 修改播放图标
            self.process_value = 0 # 重置进度值

            # 获取网络歌曲
            self.get_music_thread = GetMusicThread()
            self.get_music_thread.finished_signal.connect(self.init_player)
            self.get_music_thread.start()
        except Exception as e:
            pass

    # 设置播放器
    def init_player(self,url, song_name):
        
        self.var_song_name = song_name
        self.song_name.setText(f'{self.var_song_name} - Playing')
        content = QMediaContent(QtCore.QUrl(url))
        self.player.setMedia(content)
        self.player.setVolume(50)

        self.player.play()
        self.duration = self.player.duration()  # 音乐的时长
        # 设置状态为绿色
        self.status_label.setStyleSheet('''
            QLabel{
                background:#72EA72;
                border-radius:5px;
                }
        ''')

        # 进度条计时器
        self.process_timer = QtCore.QTimer()
        self.process_timer.setInterval(1000)
        self.process_timer.start()
        self.process_timer.timeout.connect(self.process_timer_status)


    # 定时器
    def check_music_status(self):
        player_status = self.player.mediaStatus()
        player_duration = self.player.duration()
        # print("音乐时间：",player_duration)
        # print("当前播放器状态",player_status)
        if player_status == 7:
            self.next_music()

        if player_duration > 0:
            self.duration = player_duration

    # 进度条定时器
    def process_timer_status(self):
        try:
            if self.play_status is True:
                self.process_value +=float(100 / (self.duration/1000))
                self.process_bar.setValue(int(self.process_value))
        except Exception as e:
            pass


# 异步子线程获取音乐链接
class GetMusicThread(QtCore.QThread):
    finished_signal = QtCore.pyqtSignal(str,str)
    def __init__(self,parent=None):
        super().__init__(parent)
    def run(self):
        reps = requests.post("https://api.uomg.com/api/rand.music?sort=抖音榜&format=json")
        # print(reps.json())
        file_url = reps.json()['data']['url']
        song_name = reps.json()['data']['name']
        self.finished_signal.emit(file_url,song_name)


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    gui = Music()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()