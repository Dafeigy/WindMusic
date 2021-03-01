from PyQt5 import QtWidgets,QtGui,QtCore,Qt
from PyQt5.QtMultimedia import QMediaContent,QMediaPlayer
import qtawesome as qta
import requests,traceback
font=QtGui.QFont()
font.setFamily("STXihei")
font.setPointSize(20)
class Music(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400,200)
        self.setWindowTitle("🎧+📚=😊")
        self.setWindowOpacity(0.8)

        self.init_ui()
        self.custom_style()
        self.play_status = False # 播放状态初始化为否
        self.player = QMediaPlayer(self)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.check_music_status)


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
                cursor:pointer;
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

        # 标题 半成，接口部分未找到适合的
        '''
        slogan=requests.get('https://api.xygeng.cn/one').json()['data']['content']
        self.title_lable = QtWidgets.QLabel(slogan)
        self.title_lable.setFont(font)
       '''
        self.title_lable = QtWidgets.QLabel('🌥WindPlayer')
        self.title_lable.setStyleSheet('''
        QLabel{
                color:"black";
                }
        ''')
        self.title_lable.setFont(font)
        self.title_lable.setAlignment(QtCore.Qt.AlignCenter)
        # 关闭按钮
        self.close_btn = QtWidgets.QPushButton("")  # 关闭按钮
        self.close_btn.clicked.connect(self.close_btn_event)
        self.close_btn.setFixedSize(15,15)

        # 音乐状态按钮
        self.status_label = QtWidgets.QLabel("")
        # self.swith_btn.clicked.connect(self.swith_background) #此处还未完成 Darkmode 和 LightMode 的切换
        self.status_label.setFixedSize(15,15)

        # 播放按钮
        play_icon = qta.icon("fa.play-circle-o",)
        self.play_btn = QtWidgets.QPushButton(play_icon,"")
        self.play_btn.setIconSize(QtCore.QSize(80, 80))
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
        self.next_btn.setIconSize(QtCore.QSize(80,80))
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

        self.main_layout.addWidget(self.close_btn,0,0,1,1)
        self.main_layout.addWidget(self.title_lable,0,1,1,1)
        self.main_layout.addWidget(self.status_label,1,0,1,1)
        self.main_layout.addWidget(self.play_btn, 1, 1, 1, 1)
        self.main_layout.addWidget(self.next_btn, 1, 2, 1, 1)
        self.main_layout.addWidget(self.process_bar,2,0,1,3)

        self.setCentralWidget(self.main_widget)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框

    # 关闭程序
    def close_btn_event(self):
        self.close()
    # 夜间模式切换 （未完成 ）
    def swich_background(self):
        self.main_widget.setStyleSheet('''
        QWidget{
        "background-color: black"}
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
                else:
                    self.next_music()
            # 暂停音乐
            else:
                # 设置状态为蓝色
                self.status_label.setStyleSheet('''QLabel{background:#0099CC;border-radius:5px;}''')
                self.play_status = False
                self.play_btn.setIcon(qta.icon("fa.play-circle-o"))
                self.player.pause()
        except Exception as e:
            print(repr(e))

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
            print(traceback.print_exc())

    # 设置播放器
    def init_player(self,url):
        # print("获取到音乐链接：",url)
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
                #print("当前进度：",self.process_value)
                self.process_bar.setValue(self.process_value)
        except Exception as e:
            print('')
            #print(repr(e))


# 异步子线程获取音乐链接
class GetMusicThread(QtCore.QThread):
    finished_signal = QtCore.pyqtSignal(str)
    def __init__(self,parent=None):
        super().__init__(parent)
    def run(self):
        reps = requests.post("https://api.uomg.com/api/rand.music?sort=抖音榜&format=json")
        # print(reps.json())
        file_url = reps.json()['data']['url']
        self.finished_signal.emit(file_url)


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    gui = Music()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()