# coding=utf-8
from PIL import Image
import numpy as np
import itchat
import os


def save_avatar(folder):
    """
    保存微信好友头像
    :param folder: 保存的文件夹
    """
    itchat.auto_login(hotReload=True)
    users = itchat.get_friends() or []
    print('%d friends found.' % len(users))
    if not os.path.exists(folder):
        os.makedirs(folder)
    index = 1
    for i, user in enumerate(users):
        nickname = user.RemarkName
        username = user.UserName
        file_path = os.path.join(folder, '%03d_%s.png' % (i, nickname))
        if not os.path.isfile(file_path):  # 不重复下载
            avatar = itchat.get_head_img(username)
            with open(file_path, 'w') as f:
                f.write(avatar)
                print('Download %d: %s' % (index, file_path))
                index += 1


def join_images(image_files, rows, cols, width, height, save_file=None):
    """
    拼接操作
    :param image_files: 待拼接的图片
    :param rows: 行数
    :param cols: 列数
    :param width: 每张小头像的宽度
    :param height: 每张小头像的高度
    :param save_file: 拼接好图片的保存路径
    """
    canvas = np.ones((height * rows, width * cols, 3), np.uint8)
    for row in range(rows):
        for col in range(cols):
            index = row * cols + col
            if index >= len(image_files):
                break
            file_path = image_files[index]
            im = Image.open(file_path)
            im = im.resize((width, height))
            im_data = np.array(im)
            if len(im_data.shape) == 2:
                im_data = np.expand_dims(im_data, -1)
            x = col * width
            y = row * height
            canvas[y: y + height, x: x + width, :] = im_data
    image = Image.fromarray(canvas)
    image.show()
    if save_file:
        image.save(save_file)


def get_image_files(folder, filters=None):
    """
    取出待拼接头像
    :param folder: 目标文件夹
    :param filters: 需要过滤的图片
    :return: 头像路径
    """
    filters = filters or []
    filenames = [os.path.join(folder, sub) for sub in os.listdir(folder)
                 if sub.endswith('.png') and not filters.__contains__(sub)]
    return filenames


def calculate_align_way(image_num, force_align=False):
    """
    计算图片排版对齐方式
    :param image_num: 图片数量
    :return: (rowls, columns)
    """
    actual_value = image_num ** 0.5
    suggest_value = int(actual_value)
    if actual_value == suggest_value or force_align:
        return suggest_value, suggest_value
    else:
        return suggest_value, suggest_value + 1


FOLDER = 'avatars'

if __name__ == '__main__':
    # 保存所有好友头像
    save_avatar(FOLDER)

    # 取到准备拼接的头像
    image_files = get_image_files(FOLDER)

    # 计算拼接的行列
    rows, columns = calculate_align_way(len(image_files), force_align=True)

    # 执行拼接操作
    join_images(image_files, rows, columns, 64, 64, 'result.png')
