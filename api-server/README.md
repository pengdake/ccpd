## 运行api服务

```bash
python api.py --model_path <model_path> --model_type <model_type>
```

model_path: 模型文件的路径。
model_type: 模型类型，支持gru或者wrnn

例如：
```bash
python /root/data/storage_name/code/ccpd/api-server/api.py --model_path /root/data/storage_name/model --model_type wrnn
```
