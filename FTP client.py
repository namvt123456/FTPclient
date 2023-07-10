from ftplib import FTP, FTP_PORT, FTP_TLS
import socket


def send_command(ftp, command):
    # Gửi lệnh tới server và nhận phản hồi
    ftp.sendcmd(command)


def send_epsv_command(ftp):
    # Gửi lệnh EPSV và nhận phản hồi
    response = ftp.sendcmd('EPSV')
    return response


def send_pasv_command(ftp):
    # Gửi lệnh PASV và nhận phản hồi
    response = ftp.sendcmd('PASV')
    return response


def parse_pasv_response(response):
    # Phân tích phản hồi PASV để lấy địa chỉ IP và cổng
    start = response.find('(') + 1
    end = response.find(')')
    address = response[start:end]
    parts = address.split(',')
    ip_address = '.'.join(parts[:4])
    port = (int(parts[4]) << 8) + int(parts[5])
    return ip_address, port


def upload_file(hostname, username, password, file_path):
    # Kết nối tới server FTP
    ftp = FTP()

    # Sử dụng FTP_TLS để hỗ trợ FTPS (FTP over TLS/SSL)
    ftps_mode = False
    try:
        ftp = FTP_TLS(hostname)
        ftps_mode = True
    except socket.gaierror:
        ftp.connect(hostname)

    # Đăng nhập với tên người dùng và mật khẩu
    ftp.login(username, password)

    # Kiểm tra và thiết lập chế độ truyền tải tệp tin (PASV hoặc EPSV)
    if ftps_mode:
        ftp.prot_p()
    elif ftp.has_ext('EPSV'):
        send_command(ftp, 'EPSV')
    else:
        send_command(ftp, 'PASV')

    # Mở file cần upload
    with open(file_path, 'rb') as file:
        # Upload file lên server
        if ftps_mode:
            ftp.storbinary('STOR ' + file_path, file)
        else:
            response = send_pasv_command(ftp)
            ip_address, port = parse_pasv_response(response)
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.connect((ip_address, port))
            ftp.storbinary('STOR ' + file_path, file, socket=data_socket)
            data_socket.close()

    # Đóng kết nối FTP
    ftp.quit()



hostname = 'ftp.dungngu.com'
username = 'dungngu0312 '
password = 'dung0312'
file_path = 'dungngu.txt'  # Đường dẫn tới file cần upload

upload_file(hostname, username, password, file_path)
