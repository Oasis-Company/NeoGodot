"""Hybrid Retriever combining vector and keyword search with RRF fusion."""

import asyncio
from typing import Dict, List, Optional
import logging
from collections import defaultdict
from context_engine.types import RetrievedItem, QueryIntent

logger = logging.getLogger(__name__)


class HybridRetriever:
    """混合检索器，结合向量检索和关键词检索，使用 RRF 融合"""
    
    RRF_CONFIG = {
        "k": 60,
        "vector_weight": 0.6,
        "keyword_weight": 0.4,
    }
    
    def __init__(self, vector_store=None):
        self.vector_store = vector_store
        self._keyword_index = defaultdict(list)
        self._documents = {}
    
    def add_documents(self, documents: List[RetrievedItem]) -> None:
        """添加文档到检索器"""
        for doc in documents:
            doc_id = f"{doc.source_path}:{hash(doc.content)}"
            self._documents[doc_id] = doc
            self._index_keywords(doc.content, doc_id)
    
    def _index_keywords(self, content: str, doc_id: str) -> None:
        """简单关键词索引"""
        words = content.lower().split()
        for word in set(words):
            if len(word) > 2:
                self._keyword_index[word].append(doc_id)
    
    async def retrieve(
        self,
        query: str,
        intent: Optional[QueryIntent] = None,
        top_k: int = 10,
    ) -> List[RetrievedItem]:
        """执行混合检索
        
        Args:
            query: 查询字符串
            intent: 查询意图（可选）
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        vector_task = self._vector_search(query, top_k * 2)
        keyword_task = self._keyword_search(query, top_k * 2)
        
        vector_results, keyword_results = await asyncio.gather(
            vector_task, keyword_task, return_exceptions=True
        )
        
        if isinstance(vector_results, Exception):
            logger.warning(f"Vector search failed: {vector_results}")
            vector_results = []
        if isinstance(keyword_results, Exception):
            logger.warning(f"Keyword search failed: {keyword_results}")
            keyword_results = []
        
        fused_results = self._rrf_fusion(vector_results, keyword_results, top_k)
        
        return fused_results
    
    async def _vector_search(self, query: str, top_k: int) -> List[RetrievedItem]:
        """向量检索（模拟实现）"""
        if self.vector_store:
            try:
                return await self.vector_store.search(query, top_k)
            except Exception as e:
                logger.warning(f"Vector store search failed: {e}")
        
        return []
    
    async def _keyword_search(self, query: str, top_k: int) -> List[RetrievedItem]:
        """关键词检索"""
        query_words = query.lower().split()
        doc_scores = defaultdict(float)
        
        for word in query_words:
            if word in self._keyword_index:
                for doc_id in self._keyword_index[word]:
                    doc_scores[doc_id] += 1.0
        
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in sorted_docs[:top_k]:
            doc = self._documents.get(doc_id)
            if doc:
                results.append(RetrievedItem(
                    content=doc.content,
                    source_type=doc.source_type,
                    source_path=doc.source_path,
                    relevance_score=min(1.0, score / len(query_words)),
                    metadata=doc.metadata,
                ))
        
        return results
    
    def _rrf_fusion(
        self,
        vector_results: List[RetrievedItem],
        keyword_results: List[RetrievedItem],
        top_k: int,
    ) -> List[RetrievedItem]:
        """Reciprocal Rank Fusion 融合"""
        k = self.RRF_CONFIG["k"]
        weights = {
            "vector": self.RRF_CONFIG["vector_weight"],
            "keyword": self.RRF_CONFIG["keyword_weight"],
        }
        
        scores: Dict[str, float] = {}
        items: Dict[str, RetrievedItem] = {}
        
        for rank, item in enumerate(vector_results):
            key = f"{item.source_path}:{hash(item.content)}"
            scores[key] = scores.get(key, 0) + weights["vector"] / (k + rank + 1)
            items[key] = item
        
        for rank, item in enumerate(keyword_results):
            key = f"{item.source_path}:{hash(item.content)}"
            scores[key] = scores.get(key, 0) + weights["keyword"] / (k + rank + 1)
            items[key] = item
        
        sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
        
        result = []
        for key in sorted_keys[:top_k]:
            item = items[key]
            item.relevance_score = scores[key]
            result.append(item)
        
        return result
