# Genomics Analysis in R

## Overview

Comprehensive genomics and bioinformatics statistical methods using Bioconductor packages. Covers differential expression analysis, pathway enrichment, and visualization for RNA-seq and microarray data.

## Bioconductor Setup

```r
# Install Bioconductor
if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")

# Install packages
BiocManager::install(c(
  "DESeq2",
  "edgeR",
  "limma",
  "clusterProfiler",
  "org.Hs.eg.db",
  "EnhancedVolcano",
  "ComplexHeatmap"
))
```

## RNA-seq Differential Expression

### DESeq2 Analysis

```r
library(DESeq2)

# Create DESeqDataSet from count matrix
dds <- DESeqDataSetFromMatrix(
  countData = count_matrix,
  colData = sample_info,
  design = ~ condition
)

# Filter low counts
keep <- rowSums(counts(dds) >= 10) >= min_samples
dds <- dds[keep, ]

# Run DESeq2
dds <- DESeq(dds)

# Get results
res <- results(dds, contrast = c("condition", "treatment", "control"))

# Shrink log fold changes (for visualization)
res_shrunk <- lfcShrink(dds, coef = "condition_treatment_vs_control", type = "apeglm")

# Summary
summary(res)

# Significant genes
sig_genes <- subset(res, padj < 0.05 & abs(log2FoldChange) > 1)
```

### DESeq2 with Multiple Factors

```r
# Multi-factor design
dds <- DESeqDataSetFromMatrix(
  countData = count_matrix,
  colData = sample_info,
  design = ~ batch + condition  # Control for batch
)

dds <- DESeq(dds)

# Results controlling for batch
res <- results(dds, contrast = c("condition", "treatment", "control"))
```

### edgeR Analysis

```r
library(edgeR)

# Create DGEList
dge <- DGEList(counts = count_matrix, group = sample_info$condition)

# Filter low expression
keep <- filterByExpr(dge)
dge <- dge[keep, , keep.lib.sizes = FALSE]

# Normalize
dge <- calcNormFactors(dge)

# Estimate dispersion
design <- model.matrix(~ condition, data = sample_info)
dge <- estimateDisp(dge, design)

# Fit model
fit <- glmQLFit(dge, design)

# Test
qlf <- glmQLFTest(fit, coef = 2)

# Top genes
topTags(qlf, n = 20)
```

### limma-voom for RNA-seq

```r
library(limma)

# Create DGEList
dge <- DGEList(counts = count_matrix)
dge <- calcNormFactors(dge)

# Design matrix
design <- model.matrix(~ condition, data = sample_info)

# voom transformation
v <- voom(dge, design, plot = TRUE)

# Fit model
fit <- lmFit(v, design)
fit <- eBayes(fit)

# Results
results <- topTable(fit, coef = 2, number = Inf)

# Significant genes
sig_genes <- results[results$adj.P.Val < 0.05, ]
```

## Visualization

### Volcano Plots

```r
library(EnhancedVolcano)

EnhancedVolcano(
  res,
  lab = rownames(res),
  x = "log2FoldChange",
  y = "pvalue",
  xlim = c(-5, 5),
  ylim = c(0, -log10(min(res$pvalue, na.rm = TRUE))),
  pCutoff = 0.05,
  FCcutoff = 1,
  pointSize = 2,
  labSize = 4,
  title = "Differential Expression",
  subtitle = "Treatment vs Control"
)
```

### MA Plots

```r
# DESeq2
plotMA(res, ylim = c(-5, 5))

# With highlighting
plotMA(res_shrunk, ylim = c(-5, 5))
```

### Heatmaps

```r
library(ComplexHeatmap)
library(circlize)

# Get top DE genes
top_genes <- head(order(res$padj), 50)

# Normalized counts
vsd <- vst(dds, blind = FALSE)
mat <- assay(vsd)[top_genes, ]
mat <- t(scale(t(mat)))  # Z-score by row

# Create heatmap
Heatmap(
  mat,
  name = "Z-score",
  col = colorRamp2(c(-2, 0, 2), c("blue", "white", "red")),
  show_row_names = TRUE,
  show_column_names = TRUE,
  cluster_rows = TRUE,
  cluster_columns = TRUE,
  top_annotation = HeatmapAnnotation(
    Condition = sample_info$condition,
    col = list(Condition = c("control" = "blue", "treatment" = "red"))
  )
)
```

### PCA Plots

```r
# Using DESeq2
plotPCA(vsd, intgroup = "condition")

# Custom PCA
pca_data <- plotPCA(vsd, intgroup = "condition", returnData = TRUE)
ggplot(pca_data, aes(x = PC1, y = PC2, color = condition)) +
  geom_point(size = 3) +
  theme_bw() +
  labs(title = "PCA of Samples")
```

## Pathway and Gene Set Analysis

### Gene Ontology Enrichment

```r
library(clusterProfiler)
library(org.Hs.eg.db)

# Get significant gene list
sig_genes <- rownames(subset(res, padj < 0.05 & log2FoldChange > 1))

# Convert to Entrez IDs
gene_ids <- bitr(sig_genes, fromType = "SYMBOL", toType = "ENTREZID",
                 OrgDb = org.Hs.eg.db)

# GO enrichment
go_result <- enrichGO(
  gene = gene_ids$ENTREZID,
  OrgDb = org.Hs.eg.db,
  ont = "BP",  # Biological Process
  pAdjustMethod = "BH",
  pvalueCutoff = 0.05,
  qvalueCutoff = 0.05
)

# Visualize
dotplot(go_result, showCategory = 20)
barplot(go_result, showCategory = 20)
cnetplot(go_result, categorySize = "pvalue")
```

### KEGG Pathway Analysis

```r
# KEGG enrichment
kegg_result <- enrichKEGG(
  gene = gene_ids$ENTREZID,
  organism = "hsa",
  pvalueCutoff = 0.05
)

dotplot(kegg_result, showCategory = 20)

# Pathway visualization
library(pathview)
pathview(
  gene.data = gene_fc,  # Named vector of log2FC
  pathway.id = "hsa04110",  # Cell cycle
  species = "hsa"
)
```

### Gene Set Enrichment Analysis (GSEA)

```r
library(clusterProfiler)

# Ranked gene list (all genes, ranked by log2FC or stat)
gene_list <- res$log2FoldChange
names(gene_list) <- rownames(res)
gene_list <- sort(gene_list, decreasing = TRUE)

# GSEA
gsea_result <- gseGO(
  geneList = gene_list,
  OrgDb = org.Hs.eg.db,
  ont = "BP",
  minGSSize = 10,
  maxGSSize = 500,
  pvalueCutoff = 0.05,
  verbose = FALSE
)

# Visualize
gseaplot2(gsea_result, geneSetID = 1:3)
ridgeplot(gsea_result)
```

## Microarray Analysis

### Preprocessing with affy

```r
library(affy)

# Read CEL files
raw_data <- ReadAffy(celfile.path = "data/")

# Quality control
image(raw_data[, 1])
hist(raw_data)
boxplot(raw_data)

# RMA normalization
eset <- rma(raw_data)

# Get expression matrix
expr_matrix <- exprs(eset)
```

### limma for Microarray

```r
library(limma)

# Design matrix
design <- model.matrix(~ 0 + condition, data = sample_info)
colnames(design) <- levels(sample_info$condition)

# Fit model
fit <- lmFit(expr_matrix, design)

# Contrasts
contrast_matrix <- makeContrasts(
  treatment_vs_control = treatment - control,
  levels = design
)

fit2 <- contrasts.fit(fit, contrast_matrix)
fit2 <- eBayes(fit2)

# Results
results <- topTable(fit2, coef = "treatment_vs_control", number = Inf)
```

## Batch Effect Correction

### ComBat

```r
library(sva)

# Combat batch correction
combat_data <- ComBat(
  dat = expr_matrix,
  batch = sample_info$batch,
  mod = model.matrix(~ condition, data = sample_info)
)
```

### limma removeBatchEffect

```r
library(limma)

# For visualization (not for DE analysis)
corrected <- removeBatchEffect(
  expr_matrix,
  batch = sample_info$batch,
  design = model.matrix(~ condition, data = sample_info)
)
```

## Single-Cell RNA-seq

### Seurat Workflow

```r
library(Seurat)

# Create Seurat object
seurat_obj <- CreateSeuratObject(
  counts = count_matrix,
  project = "project_name",
  min.cells = 3,
  min.features = 200
)

# QC
seurat_obj[["percent.mt"]] <- PercentageFeatureSet(seurat_obj, pattern = "^MT-")
VlnPlot(seurat_obj, features = c("nFeature_RNA", "nCount_RNA", "percent.mt"))

# Filter
seurat_obj <- subset(seurat_obj,
                     subset = nFeature_RNA > 200 &
                              nFeature_RNA < 5000 &
                              percent.mt < 20)

# Normalize
seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj, nfeatures = 2000)

# Scale and PCA
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj)

# Clustering
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:20)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)

# UMAP
seurat_obj <- RunUMAP(seurat_obj, dims = 1:20)
DimPlot(seurat_obj, reduction = "umap")

# Find markers
markers <- FindAllMarkers(seurat_obj, only.pos = TRUE)
```

## GWAS Analysis

### Basic Association Testing

```r
# Simple association test
gwas_results <- apply(genotype_matrix, 2, function(snp) {
  fit <- glm(phenotype ~ snp + covariates, family = binomial)
  summary(fit)$coefficients["snp", ]
})

# Manhattan plot
library(qqman)
manhattan(gwas_results, chr = "CHR", bp = "BP", p = "P", snp = "SNP")
qq(gwas_results$P)
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| DESeq2 | RNA-seq differential expression |
| edgeR | RNA-seq analysis |
| limma | Microarray and RNA-seq |
| clusterProfiler | Pathway analysis |
| EnhancedVolcano | Volcano plots |
| ComplexHeatmap | Advanced heatmaps |
| Seurat | Single-cell RNA-seq |
| sva | Batch correction |
| qqman | GWAS visualization |
