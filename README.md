# Elastic-and-Parallel-Rec-System-pipeline
Elastic recommendation system is serving for the course project for CSCI 596.
The main purpose is to use parallel computing ideas in the course to improve the performance of original monolithic client server recommendation system
## Cloud native recommendation system
### framework
1. Data Ingestion: spark and flink for real-time processing data pipeline
2. Model server: Flink
3. Model training system: pytorch

### feature
1. high performance server: async io and auto scaling
![Parameter Server](https://github.com/ZhiHanZ/Elastic-and-Parallel-Rec-System-pipeline/blob/main/resources/webroot/fg11.png)


2. distributed training using machine learning server cluster

![Parameter Server](https://github.com/ZhiHanZ/Elastic-and-Parallel-Rec-System-pipeline/blob/main/resources/webroot/fg14.png)
