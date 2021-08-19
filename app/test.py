import requests


try:
  response = requests.get("https://i.imgur.com/Gpe99Gx.png")
  file = open("static/product_images/1.png", "wb")
  file.write(response.content)
  file.close()
except:
  print("An exception occurred")
