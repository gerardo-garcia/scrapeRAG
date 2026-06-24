# README

ScrapeRAG es una herramienta de procesamiento de contenido web diseñada para transformar scrapes masivos de sitios completos en datasets optimizados para sistemas de Retrieval-Augmented Generation (RAG).

Su objetivo es eliminar el ruido típico del crawling web (HTML duplicado, assets estáticos, navegación repetitiva y contenido irrelevante) y convertir miles de URLs en documentos semánticos limpios, estructurados y listos para indexación vectorial.

La herramienta realiza un pipeline completo de:

- filtrado de recursos no textuales (CSS, JS, imágenes, fuentes)
- extracción del contenido principal de páginas HTML
- deduplicación y detección de plantillas repetidas
- normalización y limpieza del texto
- agrupación de contenido en documentos lógicos coherentes
- chunking optimizado para embeddings

El resultado es un conjunto compacto de documentos de alta calidad que mejora la precisión de búsqueda, reduce el ruido semántico y optimiza el coste de indexación en sistemas RAG modernos.

