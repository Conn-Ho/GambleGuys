import requests

url = "https://api.siliconflow.cn/v1/images/generations"

payload = {
    "model": "Kwai-Kolors/Kolors",
    "prompt": "an island near sea, with seagulls, moon shining over the sea, light house, boats int he background, fish flying over the sea",
    "image_size": "1024x1024",
    "batch_size": 1,
    "num_inference_steps": 20,
    "guidance_scale": 7.5
}
headers = {
    "Authorization": "Bearer sk-rpbdfcumdlwdfssveutdyweficaabukciujbkoltmdsnjiba",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)