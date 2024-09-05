from utils.databaseMG import *

# data = updateUserFromID("Gz7Xjg","Joynaaai","//thirdwx.qlogo.cn/mmopen/vi_32/PiajxSqBRaEKPNGnsCiag7G0tHcOMELx8ssM7Jc333TMDW0b5nTFrfXHUicb1ibKglYvZT1XtswR9j2UXkJA4CcgMyyZLH6udg7Ltia5qbETYqRnrAx0o05JphQ/132")

# data= updateCupdatetime("1864185096",1815)
data=searchThread("你")
def cursor_to_text(cursor):
    # 遍历游标中的每个文档，将其转换为字符串并逐行拼接
    result = ""
    for document in cursor.limit(5):
        # 将每个文档转换为字符串，并添加换行符
        result += str(document) + "\n"
    return result

print(cursor_to_text(data))
print(getUser("Gz7Xjg"))