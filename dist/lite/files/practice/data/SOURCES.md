
## breast_gds4057_expr_top1000.csv、breast_gds4057_samples.csv
- 来源：NCBI GEO 数据集 GDS4057（系列 GSE22093，平台 GPL96），https://ftp.ncbi.nlm.nih.gov/geo/datasets/GDS4nnn/GDS4057/soft/GDS4057_full.soft.gz
- 许可：NCBI 对 GEO 数据的使用与再分发不设限制（https://www.ncbi.nlm.nih.gov/home/about/policies/）；原始提交者可能保留权利，使用时请引用原文。
- 引用：Iwamoto T, Bianchini G, et al. Gene pathways associated with prognosis and chemotherapy sensitivity in molecular subtypes of breast cancer. J Natl Cancer Inst. 2011;103:264–272. doi:10.1093/jnci/djq524（GDS4057 记录所引文献，PubMed 21191116）。
- 处理：103 例化疗前乳腺癌活检（HER2 阴性；ER 阳性 42、阴性 56、缺失 5）。去掉 AFFX 对照、多基因探针和没有基因名的探针（余 13,650 个基因）；同一基因取平均表达最高的探针；保留平均表达不低于中位数的基因中方差最大的 1000 个；数值为 GDS 提供的转换后表达值，保留三位小数。样本表含 ER（IHC）、BMN 分级、T 分期与化疗后病理反应（GDS 子集注释）。
- 下载日期：2026-11-20

## string_human_physical_v12_s700.csv
- 来源：STRING v12.0 人类物理相互作用子网络，https://stringdb-downloads.org/download/protein.physical.links.v12.0/9606.protein.physical.links.v12.0.txt.gz，名称映射自 9606.protein.info.v12.0.txt.gz
- 许可：CC BY 4.0（https://string-db.org/cgi/access）
- 引用：Szklarczyk D, et al. The STRING database in 2023: protein–protein association networks and functional enrichment analyses for any sequenced genome of interest. Nucleic Acids Res. 2023;51(D1):D638–D646.
- 处理：保留 combined_score ≥ 700 的边，蛋白 ID 换成 STRING 首选基因名，去自环与重复边；86,519 条边、10,746 个蛋白。
- 下载日期：2026-11-20

## string_multichannel_disease_genes_v12_5.csv
- 来源：STRING API v12.5（https://string-db.org/api/tsv/network，species=9606，required_score=400），输入为 opentargets_disease_genes_ga.csv 中遗传关联分数 ≥ 0.7 的 724 个基因
- 许可：CC BY 4.0（https://string-db.org/cgi/access）
- 引用：同上（Szklarczyk et al. 2023）。
- 处理：每对基因保留一行，列出综合分数与 experiments、database、textmining、coexpression 四个证据通道分数；6,639 条边。
- 下载日期：2026-11-20

## opentargets_disease_genes_ga.csv
- 来源：Open Targets Platform GraphQL API（数据版本 26.09），https://api.platform.opentargets.org/api/v4/graphql，查询 disease.associatedTargets(orderByScore: "genetic_association")
- 许可：Open Targets Platform 数据为 CC0 1.0（https://platform-docs.opentargets.org/licence）
- 引用：Buniello A, et al. Open Targets Platform: facilitating therapeutic hypotheses building in drug discovery. Nucleic Acids Res. 2025;53(D1):D1467–D1475.
- 处理：11 种疾病（哮喘、2 型糖尿病、阿尔茨海默病、类风湿关节炎、克罗恩病、溃疡性结肠炎、精神分裂症、冠状动脉疾病、系统性红斑狼疮、银屑病、双相障碍），每种取按遗传关联分数排序的前 1500 个靶点，保留遗传关联分数 ≥ 0.5 的基因，共 2,727 行。
- 下载日期：2026-11-20

## opentargets_drug_targets.csv
- 来源：Open Targets Platform GraphQL API（数据版本 26.09）的 drug.mechanismsOfAction 与 drug.indications；作用机制数据源自 ChEMBL
- 许可：Open Targets 数据 CC0 1.0；作用机制源自 ChEMBL（CC BY-SA 3.0），本表随之按 CC BY-SA 3.0 提供。
- 引用：同上（Buniello et al. 2025）；Zdrazil B, et al. The ChEMBL Database in 2023. Nucleic Acids Res. 2024;52(D1):D1180–D1192.
- 处理：17 种药物的作用机制靶点（二甲双胍因靶点为 50 余个线粒体亚基、机制不确定而未收录）；approved_for 只列出与上表 11 种疾病 ID 完全一致、且临床阶段为 APPROVAL 的适应症，其他适应症未列出。
- 下载日期：2026-11-20

## biogrid_human_dna_repair_records.csv
- 来源：BioGRID 5.0.263，BIOGRID-ORGANISM-5.0.263.tab3.zip 中的 BIOGRID-ORGANISM-Homo_sapiens-5.0.263.tab3.txt，https://downloads.thebiogrid.org/BioGRID/Release-Archive/BIOGRID-5.0.263/
- 许可：MIT 许可证（https://wiki.thebiogrid.org/doku.php/terms_and_conditions）
- 引用：Oughtred R, et al. The BioGRID interaction database: 2019 update. Nucleic Acids Res. 2019;47(D1):D529–D541. doi:10.1093/nar/gky1079
- 处理：只保留两个相互作用者都是人类、且都属于 Reactome 通路 R-HSA-73894“DNA Repair”（Reactome 第 98 版，346 个基因）的记录；未合并重复记录，保留每条原始记录的官方基因符号、实验方法、物理/遗传类型、通量和文献编号。共 18,308 条记录，对应 5,052 个不同基因对（含自身相互作用）、304 个基因。
- 下载日期：2026-11-20

## reactome_selected_pathways.csv
- 来源：Reactome 第 98 版通路基因集 ReactomePathways.gmt，https://reactome.org/download/current/ReactomePathways.gmt.zip
- 许可：Reactome 数据为 CC0 1.0（https://reactome.org/license）
- 引用：Milacic M, et al. The Reactome Pathway Knowledgebase 2024. Nucleic Acids Res. 2024;52(D1):D672–D678. doi:10.1093/nar/gkad1025
- 处理：选取 8 条功能差异明显的通路（Complex I biogenesis、Cytosolic tRNA aminoacylation、Proteasome assembly、Cholesterol biosynthesis、Activation of the pre-replicative complex、Mitochondrial translation elongation、Citric acid cycle (TCA cycle)、Collagen formation），每行一个“通路–基因”对，共 432 行；属于多条所选通路的基因原样保留，由使用者处理。
- 下载日期：2026-11-20

## collectri_human_tf_target_ccby_curated.csv
- 来源：CollecTRI 人类 TF–靶基因调控关系，经 OmniPath 网络服务下载：https://omnipathdb.org/interactions?datasets=collectri&genesymbols=yes&fields=sources,references,curation_effort&format=tsv（64,516 行）
- 许可：CollecTRI 在 OmniPath 中标为组合资源（各条关系沿用来源数据库的许可，https://omnipathdb.org/resources）。本文件只保留至少有一个 CC BY 4.0 人工整理来源支持的关系（NTNU.Curated、TFactS、SIGNOR、CytReg、Pavlidis2021、GOA、IntAct，均为 OmniPath 资源表中的 CC BY 4.0），按 CC BY 4.0 提供。
- 引用：Müller-Dott S, et al. Expanding the coverage of regulons from high-confidence prior knowledge for accurate estimation of transcription factor activities. Nucleic Acids Res. 2023;51(20):10934–10949. doi:10.1093/nar/gkad841；Türei D, et al. Integrated intra- and intercellular signaling knowledge for multicellular omics analysis. Mol Syst Biol. 2021;17:e9923.
- 处理：去掉调控方为蛋白复合物（COMPLEX:）的行；每个 (tf, target) 只保留一行；列为 tf、target（HGNC 基因符号）、对应 UniProt 编号，cc_by_curated 列出支持该关系的 CC BY 4.0 来源；未保留调控符号（激活/抑制）。共 16,164 行、918 个 TF、4,338 个基因（含 1 条自调控）。
- 下载日期：2026-11-20

## yeast_string_physical_v12_hc.csv、yeast_string_physical_v12_nodes.csv
- 来源：STRING v12.0 酿酒酵母（4932）物理相互作用子网络 https://stringdb-downloads.org/download/protein.physical.links.v12.0/4932.protein.physical.links.v12.0.txt.gz 与蛋白信息 https://stringdb-downloads.org/download/protein.info.v12.0/4932.protein.info.v12.0.txt.gz
- 许可：CC BY 4.0（https://string-db.org/cgi/access）
- 引用：Szklarczyk D, et al. The STRING database in 2023. Nucleic Acids Res. 2023;51(D1):D638–D646. doi:10.1093/nar/gkac1000
- 处理：保留 combined_score ≥ 700 的边，每对蛋白一行（protein1 < protein2）；去掉编号前缀“4932.”；节点表只含出现在边表中的 3,384 个蛋白，注释只保留第一句并截断至 80 字符。共 43,030 条边。
- 下载日期：2026-11-20

## hpa_celline_rna_panel56.csv
- 来源：Human Protein Atlas 细胞系 RNA-seq 数据 rna_celline.tsv（压缩包内文件日期 2023-05-24），https://www.proteinatlas.org/download/tsv/rna_celline.tsv.zip
- 许可：HPA 数据库中可受版权保护的部分为 CC BY 4.0（https://www.proteinatlas.org/about/licence）；细胞系转录组为 HPA 自产数据。
- 引用：Uhlén M, et al. Tissue-based map of the human proteome. Science. 2015;347:1260419. doi:10.1126/science.1260419；Jin H, et al. Systematic transcriptional analysis of human cell lines for gene expression landscape and tumor representation. Nat Commun. 2023. doi:10.1038/s41467-023-41132-w；数据来自 proteinatlas.org。
- 处理：只保留 56 个按标记基因先验分组挑选的基因（上皮、间质、造血、MHC II、增殖、神经/神经内分泌、干扰素刺激各 8 个，按此顺序排列），整理为 1,206 个细胞系 × 56 个基因的 nTPM 宽表，保留一位小数。
- 下载日期：2026-11-20

## lausanne68_sc_fc.csv
- 来源：Griffa A, Alemán-Gómez Y, Hagmann P. Structural and functional connectome from 70 young healthy adults. Zenodo, 2019. doi:10.5281/zenodo.2872624（文件 Individual_Connectomes.mat），https://zenodo.org/records/2872624
- 许可：CC BY 4.0（Zenodo 记录所标许可）
- 引用：上述 Zenodo 数据集；数据说明中的方法文献包括 Hagmann P, et al. Mapping the structural core of human cerebral cortex. PLoS Biol. 2008;6:e159；Cammoun L, et al. Mapping the human connectome at multiple scales with diffusion spectrum MRI. J Neurosci Methods. 2012;203:386–397。
- 处理：只取最粗尺度（68 个皮层区，Desikan–Killiany 皮层分区）的个体结构连接（DSI 确定性追踪的纤维密度，按流线长度与两区表面积归一化）和个体静息态功能连接（皮尔逊相关）。第 34 号被试（从 1 计数）的 FC 全为缺失值，SC 与 FC 均去掉该被试，余 69 人。每行一名被试的一种模态（modality = SC 或 FC），列为上三角各边（列名 "i-j"，0 ≤ i < j ≤ 67，与 numpy.triu_indices(68, 1) 顺序一致）；SC 保留 4 位有效数字，FC 保留 3 位小数。原文件不含脑区名称；据数据核对，节点 i 与 i+34（i < 34）为两半球的同源脑区（每个节点在对侧半球中 FC 最强的伙伴都是它），但哪一侧为左半球未经核实。
- 下载日期：2026-11-20

## eeg_eyes_open_closed.csv
- 来源：PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0，https://physionet.org/content/eegmmidb/1.0.0/（文件 S001R01.edf … S006R02.edf）
- 许可：Open Data Commons Attribution License v1.0（ODC-By 1.0，https://opendatacommons.org/licenses/by/1-0/），再分发需注明出处
- 引用：Schalk G. EEG Motor Movement/Imagery Dataset (version 1.0.0). PhysioNet. 2009. doi:10.13026/C28G6P；Schalk G, McFarland DJ, Hinterberger T, Birbaumer N, Wolpaw JR. BCI2000: a general-purpose brain-computer interface (BCI) system. IEEE Trans Biomed Eng. 2004;51:1034–1043；Goldberger AL, et al. PhysioBank, PhysioToolkit, and PhysioNet. Circulation. 2000;101:e215–e220。
- 处理：前 6 名被试（S001–S006）的两段 1 分钟静息基线（R01 睁眼 EO、R02 闭眼 EC）；从 64 导中取 19 个 10-20 系统位置（Fp1 Fp2 F7 F3 Fz F4 F8 T7 C3 Cz C4 T8 P7 P3 Pz P4 P8 O1 O2）；每段取前 60 s（9600 点），用零相位 FIR 抗混叠滤波后从 160 Hz 降采样到 80 Hz（scipy.signal.decimate），取整到 1 µV。每行一个采样点：subject、condition、19 个通道的电压（µV），每段 4800 行。未做伪迹剔除或重参考。
- 下载日期：2026-11-20

## nhanes_phq9_2017_2018.csv
- 来源：美国 CDC/NCHS 全国健康与营养调查 NHANES 2017–2018 周期，抑郁筛查问卷 DPQ_J（https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DPQ_J.xpt）与人口学 DEMO_J（https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.xpt）
- 许可：美国联邦政府作品，公有领域（NCHS 数据公开发布，使用时请注明来源）
- 引用：Centers for Disease Control and Prevention (CDC), National Center for Health Statistics (NCHS). National Health and Nutrition Examination Survey Data, 2017–2018. Hyattsville, MD: U.S. Department of Health and Human Services, CDC；PHQ-9 量表：Kroenke K, Spitzer RL, Williams JB. The PHQ-9: validity of a brief depression severity measure. J Gen Intern Med. 2001;16:606–613。
- 处理：DPQ010–DPQ090 九个条目重命名为 PHQ1–PHQ9（0–3 分），按 SEQN 合并性别 RIAGENDR（1 男，2 女，列名 sex）和年龄 RIDAGEYR（列名 age）；只保留 9 个条目都为 0–3 的受访者（去掉缺失、7 拒答、9 不知道），共 5,068 人；未包含抽样权重和 DPQ100。
- 下载日期：2026-11-20

## yeast_string_v12_experimental.csv、yeast_genes_essentiality.csv
- 来源：STRING v12.0 酿酒酵母（4932）完整证据通道文件 https://stringdb-downloads.org/download/protein.links.full.v12.0/4932.protein.links.full.v12.0.txt.gz 与蛋白信息 4932.protein.info.v12.0.txt.gz；必需性来自酵母基因组数据库（SGD）表型注释 https://downloads.yeastgenome.org/curation/literature/phenotype_data.tab
- 许可：STRING 为 CC BY 4.0（https://string-db.org/cgi/access）；SGD 数据为 CC BY 4.0（https://www.yeastgenome.org/）
- 引用：Szklarczyk D, et al. The STRING database in 2023. Nucleic Acids Res. 2023;51(D1):D638–D646；Engel SR, et al. New data and collaborations at the Saccharomyces Genome Database: updated reference genome, alleles, and the Alliance of Genome Resources. Genetics. 2022;220:iyab224；必需性的原始实验：Giaever G, et al. Functional profiling of the Saccharomyces cerevisiae genome. Nature. 2002;418:387–391（PMID 12140549）。
- 处理：边表只保留本物种直接实验证据通道 experiments（不含 experiments_transferred）≥ 400 的蛋白对，每对一行（orf1 < orf2），列为两个 ORF 系统名与 experiments 分数（400–999，可在案例中再提高阈值），共 57,029 条边、4,912 个蛋白。基因表含边表中的全部 ORF、STRING 首选基因名，以及 essential：SGD 中引用 PMID 12140549、突变类型 null、表型 "inviable" 记为 1，表型 "viable" 记为 0，该研究未注释的记为空（1,018 个 1、3,623 个 0、271 个空）。
- 下载日期：2026-11-20

## hospital_lyon_contacts.tsv
- 来源：SocioPatterns “Hospital ward dynamic contact network”，http://www.sociopatterns.org/datasets/hospital-ward-dynamic-contact-network/（文件 http://www.sociopatterns.org/assets/data/hospital_lyon_contacts.dat.gz）
- 许可：Creative Commons 署名–非商业性使用–相同方式共享 3.0（CC BY-NC-SA 3.0，http://creativecommons.org/licenses/by-nc-sa/3.0/，数据页所标）。仅限非商业用途再分发，须署名并沿用同一许可证；数据页要求引用下列论文、致谢 SocioPatterns 合作组并链接 www.sociopatterns.org。
- 引用：Vanhems P, Barrat A, Cattuto C, Pinton J-F, Khanafer N, Régis C, et al. Estimating potential infection transmission routes in hospital wards using wearable proximity sensors. PLoS ONE. 2013;8(9):e73970. doi:10.1371/journal.pone.0073970
- 处理：仅解压，内容未删减（32,424 行，制表符分隔，无表头，列为 t i j Si Sj；t 为秒，每行表示区间 [t−20 s, t] 内的一次活跃接触）。
- 下载日期：2026-11-20

## lausanne114_sc_edges.csv、lausanne114_nodes.csv、lausanne114_fc.csv
- 来源：Shafiei G, Markello R, Talpalaru T, Makowski C, Kirschner M, Devenyi GA, Hagmann P, Cashman NR, Lepage M, Chakravarty MM, Dagher A, Mišić B. Consensus structural and functional connectome from 70 young healthy adults. Zenodo, 2019. doi:10.5281/zenodo.3067849（文件 Consensus_Connectomes.mat），https://zenodo.org/records/3067849；该记录由个体数据集 doi:10.5281/zenodo.2872624（Griffa、Alemán-Gómez 与 Hagmann 2019）构建。
- 许可：CC BY 4.0（Zenodo 记录所标许可）
- 引用：Shafiei G, Markello RD, Makowski C, et al. Spatial patterning of tissue volume loss in schizophrenia reflects brain network architecture. Biol Psychiatry. 2020;87(8):727–735. doi:10.1016/j.biopsych.2019.09.031；个体数据与方法见 Griffa A, Alemán-Gómez Y, Hagmann P. Structural and functional connectome from 70 young healthy adults. Zenodo, 2019. doi:10.5281/zenodo.2872624。
- 处理：只取 LauConsensus.Matrices 的第 2 个尺度（Lausanne 图谱 114 个皮层区）。lausanne114_sc_edges.csv：组水平一致性结构连接的上三角非零项（1,306 条边），列为 i、j（0 起编号）、fiber_density（原文件“weighted adj mat”，即纤维密度，6 位有效数字）、length_mm（“fiber length mat”，保留 2 位小数）。lausanne114_nodes.csv：脑区名、简称、静息态子网络标签（rsn）、半球、坐标（保留 2 位小数），去掉了字符串末尾的换行符。lausanne114_fc.csv：组水平功能连接矩阵（114×114，保留 4 位小数，无表头）。
- 下载日期：2026-11-20

## yeast_ppi_biogrid.csv、yeast_genes_essential.csv
- 来源：BioGRID 5.0.263，BIOGRID-ORGANISM-5.0.263.tab3.zip 中的 BIOGRID-ORGANISM-Saccharomyces_cerevisiae_S288c-5.0.263.tab3.txt，https://downloads.thebiogrid.org/BioGRID/Release-Archive/BIOGRID-5.0.263/；必需性来自酵母基因组数据库（SGD）表型注释 https://downloads.yeastgenome.org/curation/literature/phenotype_data.tab
- 许可：BioGRID 为 MIT 许可证（https://wiki.thebiogrid.org/doku.php/terms_and_conditions）；SGD 数据为 CC BY 4.0（https://www.yeastgenome.org/ 页脚所标）
- 引用：Oughtred R, et al. The BioGRID interaction database: 2019 update. Nucleic Acids Res. 2019;47(D1):D529–D541. doi:10.1093/nar/gky1079；Engel SR, et al. New data and collaborations at the Saccharomyces Genome Database: updated reference genome, alleles, and the Alliance of Genome Resources. Genetics. 2022;220:iyab224。
- 处理：边表只保留实验类型为 physical、两个相互作用者都是 S288c（taxid 559292）、非自身相互作用、实验系统不是 Affinity Capture-RNA 或 Protein-RNA 的记录；按无序 ORF 对合并（a < b），只保留至少有 2 篇不同文献（Publication Source）支持的蛋白对；列为 a、b（ORF 系统名）、n_pub（支持文献数）、n_sys（不同实验系统数）。共 25,006 条边、3,968 个蛋白。基因表含边表中的全部 ORF、BioGRID 官方符号，以及 essential：SGD 中实验类型为 “systematic mutation set”、突变类型 null 的注释里，只有表型 “inviable” 的记为 1，只有 “viable” 的记为 0，两者都有或都没有的记为空（949 个 1、2,797 个 0、222 个空）。
- 下载日期：2026-11-20

## lausanne68_nodes.csv
- 来源：Shafiei G, et al. Consensus structural and functional connectome from 70 young healthy adults. Zenodo, 2019. doi:10.5281/zenodo.3067849（文件 Consensus_Connectomes.mat），https://zenodo.org/records/3067849；由 lausanne68_sc_fc.csv 所用的个体数据集（doi:10.5281/zenodo.2872624）构建。
- 许可：CC BY 4.0（Zenodo 记录所标许可）
- 引用：同上；Shafiei G, Markello RD, Makowski C, et al. Spatial patterning of tissue volume loss in schizophrenia reflects brain network architecture. Biol Psychiatry. 2020;87(8):727–735。
- 处理：只取 LauConsensus.Matrices 第 1 个尺度（68 个皮层区）的脑区名、简称、静息态子网络标签（rsn）、半球和坐标（保留 2 位小数，单位与坐标空间按原文件，未另行核实），去掉字符串末尾的换行符。节点顺序与 lausanne68_sc_fc.csv 一致：两文件的组水平 SC 边权相关 0.99、FC 相关 0.93（随机打乱节点顺序后约为 0）；节点 0–33 为右半球（rh），34–67 为左半球（lh），i 与 i+34 为同名脑区。
- 下载日期：2026-11-21
