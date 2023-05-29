import fitz
import os


def pdf_png(pdfPath, imagePath, zoom_x, zoom_y, rotation_angle):
    pdfDoc = fitz.open(pdfPath)
    for pg in range(pdfDoc.page_count):
        page = pdfDoc[pg]
        mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        # 判断存放图片的文件夹是否存在
        if not os.path.exists(imagePath):
            # 若图片文件夹不存在就创建
            os.makedirs(imagePath)

        pix.save(imagePath + '/' + 'grammar_tree.png')  # 将图片写入指定的文件夹内


pdf_png(r"C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.gv.pdf", r"C:/Users/YL139/Desktop/byyl/test"
                                                                           r"/byxt/TREE", 1, 1, 0)
