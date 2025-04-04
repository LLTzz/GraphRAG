#!/usr/bin/env python3
# coding: utf-8
# File: MedicalGraph.py
 

import os # os是python的一个内置模块，用于处理文件和目录
import json # json是python的一个内置模块，用于处理json格式数据
from py2neo import Graph,Node # py2neo是neo4j的python驱动，用于连接neo4j数据库，Node用于创建节点

class MedicalGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1]) # 获取当前文件路径, 并去掉文件名
        self.data_path = os.path.join(cur_dir, 'data/medical.json') # 拼接文件路径, 读取数据, 生成图谱
        self.g = Graph("neo4j://localhost:7687", auth=("neo4j", "ltz030928")) # 连接neo4j数据库

    '''读取文件'''
    def read_nodes(self):  # 读取文件
        # 共７类节点
        drugs = [] # 药品
        foods = [] #　食物
        checks = [] # 检查
        departments = [] #科室
        producers = [] #药品大类
        diseases = [] #疾病
        symptoms = []#症状

        disease_infos = []#疾病信息

        # 构建节点实体关系
        rels_department = [] #　科室－科室关系
        rels_noteat = [] # 疾病－忌吃食物关系
        rels_doeat = [] # 疾病－宜吃食物关系
        rels_recommandeat = [] # 疾病－推荐吃食物关系
        rels_commonddrug = [] # 疾病－通用药品关系
        rels_recommanddrug = [] # 疾病－热门药品关系
        rels_check = [] # 疾病－检查关系
        rels_drug_producer = [] # 厂商－药物关系

        rels_symptom = [] #疾病症状关系
        rels_acompany = [] # 疾病并发关系
        rels_category = [] #　疾病与科室之间的关系


        count = 0
        for data in open(self.data_path,encoding='utf-8'):  # 逐行读取数据，每行为一个疾病的数据
            disease_dict = {} # 存储疾病信息
            count += 1 # 计数
            print(count)
            data_json = json.loads(data) # 将json格式数据转换为字典格式，方便读取
            disease = data_json['name'] # 疾病名称
            disease_dict['name'] = disease # 疾病名称，存储到字典中
            diseases.append(disease) # 疾病名称，存储到列表中
            disease_dict['desc'] = '' # 疾病描述，初始化为空
            disease_dict['prevent'] = '' # 疾病预防，初始化为空
            disease_dict['cause'] = '' # 疾病成因，初始化为空
            disease_dict['easy_get'] = '' # 疾病易感人群，初始化为空
            disease_dict['cure_department'] = '' # 疾病所属科室，初始化为空
            disease_dict['cure_way'] = ''   # 疾病治疗方式，初始化为空
            disease_dict['cure_lasttime'] = '' # 疾病治疗周期，初始化为空
            disease_dict['symptom'] = ''    # 疾病症状，初始化为空
            disease_dict['cured_prob'] = '' # 疾病治愈概率，初始化为空

            if 'symptom' in data_json: # 症状，存储到字典中，若没有则为空
                symptoms += data_json['symptom']
                for symptom in data_json['symptom']: # 症状，存储到关系列表中，与疾病之间的关系
                    rels_symptom.append([disease, symptom]) # 疾病与症状之间的关系

            if 'acompany' in data_json: # 并发症，存储到字典中，若没有则为空
                for acompany in data_json['acompany']:
                    rels_acompany.append([disease, acompany]) # 疾病与并发症之间的关系

            if 'desc' in data_json: # 疾病描述，存储到字典中，若没有则为空
                disease_dict['desc'] = data_json['desc']

            if 'prevent' in data_json: # 疾病预防，存储到字典中，若没有则为空
                disease_dict['prevent'] = data_json['prevent']

            if 'cause' in data_json: # 疾病成因，存储到字典中，若没有则为空
                disease_dict['cause'] = data_json['cause']

            if 'get_prob' in data_json: # 疾病易感人群，存储到字典中，若没有则为空
                disease_dict['get_prob'] = data_json['get_prob']

            if 'easy_get' in data_json: # 疾病易感人群，存储到字典中，若没有则为空
                disease_dict['easy_get'] = data_json['easy_get']

            if 'cure_department' in data_json: # 疾病所属科室，存储到字典中，若没有则为空
                cure_department = data_json['cure_department'] # 疾病所属科室
                if len(cure_department) == 1: # 若只有一个科室，则将其存储到字典中
                     rels_category.append([disease, cure_department[0]]) # 疾病与科室之间的关系
                if len(cure_department) == 2: # 若有两个科室，则将其存储到字典中
                    big = cure_department[0] # 大科室
                    small = cure_department[1] # 小科室
                    rels_department.append([small, big]) # 科室与科室之间的关系
                    rels_category.append([disease, small]) # 疾病与科室之间的关系

                disease_dict['cure_department'] = cure_department # 疾病所属科室，存储到字典中
                departments += cure_department

            if 'cure_way' in data_json: # 疾病治疗方式，存储到字典中，若没有则为空
                disease_dict['cure_way'] = data_json['cure_way']

            if  'cure_lasttime' in data_json: # 疾病治疗周期，存储到字典中，若没有则为空
                disease_dict['cure_lasttime'] = data_json['cure_lasttime']

            if 'cured_prob' in data_json: # 疾病治愈概率，存储到字典中，若没有则为空
                disease_dict['cured_prob'] = data_json['cured_prob']

            if 'common_drug' in data_json: # 常用药品，存储到字典中，若没有则为空
                common_drug = data_json['common_drug']
                for drug in common_drug: # 常用药品，存储到关系列表中，与疾病之间的关系
                    rels_commonddrug.append([disease, drug])
                drugs += common_drug # 常用药品，存储到列表中

            if 'recommand_drug' in data_json: # 热门药品，存储到字典中，若没有则为空
                recommand_drug = data_json['recommand_drug']
                drugs += recommand_drug
                for drug in recommand_drug: # 热门药品，存储到关系列表中，与疾病之间的关系
                    rels_recommanddrug.append([disease, drug])

            if 'not_eat' in data_json: # 忌吃食物，存储到字典中，若没有则为空
                not_eat = data_json['not_eat']
                for _not in not_eat: # 忌吃食物，存储到关系列表中，与疾病之间的关系
                    rels_noteat.append([disease, _not])

                foods += not_eat # 忌吃食物，存储到列表中
                do_eat = data_json['do_eat'] # 宜吃食物，存储到字典中，若没有则为空
                for _do in do_eat: # 宜吃食物，存储到关系列表中，与疾病之间的关系
                    rels_doeat.append([disease, _do])

                foods += do_eat
                recommand_eat = data_json['recommand_eat'] # 推荐食谱，存储到字典中，若没有则为空

                for _recommand in recommand_eat: # 推荐食谱，存储到关系列表中，与疾病之间的关系
                    rels_recommandeat.append([disease, _recommand])
                foods += recommand_eat

            if 'check' in data_json: # 诊断检查，存储到字典中，若没有则为空
                check = data_json['check']
                for _check in check: # 诊断检查，存储到关系列表中，与疾病之间的关系
                    rels_check.append([disease, _check])
                checks += check
            if 'drug_detail' in data_json: # 药品详细信息，存储到字典中，若没有则为空
                drug_detail = data_json['drug_detail']
                producer = [i.split('(')[0] for i in drug_detail] # 生产药品
                rels_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail] # 药品与生产药品之间的关系
                producers += producer
            disease_infos.append(disease_dict)

        return set(drugs), set(foods), set(checks), set(departments), set(producers), set(symptoms), set(diseases), disease_infos,\
               rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,\
               rels_symptom, rels_acompany, rels_category # 返回节点和关系，去重，返回集合

    '''建立节点'''
    def create_node(self, label, nodes): # 创建节点，label为标签，nodes为节点
        count = 0
        for node_name in nodes: # 遍历节点
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            print(count, len(nodes))
        return

    '''创建知识图谱中心疾病的节点'''
    def create_diseases_nodes(self, disease_infos): # 创建疾病节点
        count = 0
        for disease_dict in disease_infos: # 遍历疾病信息
            node = Node("Disease", name=disease_dict['name'], desc=disease_dict['desc'],
                        prevent=disease_dict['prevent'] ,cause=disease_dict['cause'],
                        easy_get=disease_dict['easy_get'],cure_lasttime=disease_dict['cure_lasttime'],
                        cure_department=disease_dict['cure_department']
                        ,cure_way=disease_dict['cure_way'] , cured_prob=disease_dict['cured_prob']) # 疾病节点
            self.g.create(node) # 创建节点
            count += 1
            print(count) # 计数
        return

    '''创建知识图谱实体节点类型schema'''
    def create_graphnodes(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos,rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_diseases_nodes(disease_infos)
        self.create_node('Drug', Drugs)
        print(len(Drugs))
        self.create_node('Food', Foods)
        print(len(Foods))
        self.create_node('Check', Checks)
        print(len(Checks))
        self.create_node('Department', Departments)
        print(len(Departments))
        self.create_node('Producer', Producers)
        print(len(Producers))
        self.create_node('Symptom', Symptoms)
        return


    '''创建实体关系边'''
    def create_graphrels(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_relationship('Disease', 'Food', rels_recommandeat, 'recommand_eat', '推荐食谱')
        self.create_relationship('Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
        self.create_relationship('Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
        self.create_relationship('Department', 'Department', rels_department, 'belongs_to', '属于')
        self.create_relationship('Disease', 'Drug', rels_commonddrug, 'common_drug', '常用药品')
        self.create_relationship('Producer', 'Drug', rels_drug_producer, 'drugs_of', '生产药品')
        self.create_relationship('Disease', 'Drug', rels_recommanddrug, 'recommand_drug', '好评药品')
        self.create_relationship('Disease', 'Check', rels_check, 'need_check', '诊断检查')
        self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状')
        self.create_relationship('Disease', 'Disease', rels_acompany, 'acompany_with', '并发症')
        self.create_relationship('Disease', 'Department', rels_category, 'belongs_to', '所属科室')

    '''创建实体关联边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

    '''导出数据'''
    def export_data(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category = self.read_nodes()
        f_drug = open('drug.txt', 'w+')
        f_food = open('food.txt', 'w+')
        f_check = open('check.txt', 'w+')
        f_department = open('department.txt', 'w+')
        f_producer = open('producer.txt', 'w+')
        f_symptom = open('symptoms.txt', 'w+')
        f_disease = open('disease.txt', 'w+')

        f_drug.write('\n'.join(list(Drugs)))
        f_food.write('\n'.join(list(Foods)))
        f_check.write('\n'.join(list(Checks)))
        f_department.write('\n'.join(list(Departments)))
        f_producer.write('\n'.join(list(Producers)))
        f_symptom.write('\n'.join(list(Symptoms)))
        f_disease.write('\n'.join(list(Diseases)))

        f_drug.close()
        f_food.close()
        f_check.close()
        f_department.close()
        f_producer.close()
        f_symptom.close()
        f_disease.close()

        return



if __name__ == '__main__':
    handler = MedicalGraph()
    print("step1:导入图谱节点中")
    handler.create_graphnodes()
    print("step2:导入图谱边中")      
    handler.create_graphrels()
    
