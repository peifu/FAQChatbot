
import os
from urllib.parse import urlparse


def getCSVFileName(url):
    p = os.path.basename(urlparse(url).path)
    return p.replace("+", "") + ".csv"

def getQuestionTag(url):
    p = os.path.basename(urlparse(url).path)
    return p.replace("+", "")

urls = [
    "https://confluence.amlogic.com/display/SW/Chatbot+FAQ",
    "https://confluence.amlogic.com/display/SW/Security+FAQ",
    "https://confluence.amlogic.com/display/SW/TEE+FAQ",
    "https://confluence.amlogic.com/display/SW/DRM+FAQ",
    "https://confluence.amlogic.com/display/SW/VMX+CAS+FAQ",
    "https://confluence.amlogic.com/display/SW//Secure+Provision+FAQ",
    "https://confluence.amlogic.com/display/SW/001+TEE+Running+Enviroment",
    "https://confluence.amlogic.com/display/SW/002+TEE+Error+Code",
    "https://confluence.amlogic.com/display/SW/003+TEE+Debug",
    "https://confluence.amlogic.com/display/SW/004+TEE+Storage",
    "https://confluence.amlogic.com/display/SW/005+TA+Issue",
    "https://confluence.amlogic.com/display/SW/006+TDK+FAQ",

]