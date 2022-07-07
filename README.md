# campushoy-gravedigger
A program to help you get away from campushoy for NEAU only.
## 1.安装 Python
略
## 2.安装依赖
```shell
pip install pyaes
pip install pyDes
```
## 3.克隆项目
```shell
cd /opt
git clone https://github.com/lonive/campushoy-gravedigger.git
```
## 4.修改个人信息
```shell
vim /opt/campushoy-gravedigger/user.conf
```
## 5.运行
```shell
cd /opt/campushoy-gravedigger
python main.py
```
## 6.创建定时任务
```shell
crontab -e
```
添加以下内容
```shell
0 8 * * * cd /opt/campushoy-gravedigger && python main.py
```
