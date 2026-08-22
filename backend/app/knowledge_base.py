"""Knowledge Base and RAG (Retrieval Augmented Generation) Module"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import hashlib
import logging

from app.models import KnowledgeBaseItem, Organization
from app.schemas import KnowledgeBaseItemCreate, KnowledgeBaseItemUpdate

logger = logging.getLogger(__name__)


# ============================================================================
# KNOWLEDGE BASE MANAGEMENT
# ============================================================================

class KnowledgeBaseManager:
    """Manages knowledge base operations including RAG integration"""

    def __init__(self, db: Session):
        self.db = db

    def create_item(
        self,
        org_id: UUID,
        user_id: UUID,
        data: KnowledgeBaseItemCreate,
    ) -> KnowledgeBaseItem:
        """Create a knowledge base item"""
        item = KnowledgeBaseItem(
            organization_id=org_id,
            title=data.title,
            content=data.content,
            category=data.category,
            tags=data.tags or [],
            is_published=data.is_published or False,
            created_by=user_id,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        logger.info(f"Created KB item {item.id}")
        return item

    def get_item(self, org_id: UUID, item_id: UUID) -> Optional[KnowledgeBaseItem]:
        """Get a knowledge base item"""
        return self.db.query(KnowledgeBaseItem).filter(
            and_(
                KnowledgeBaseItem.organization_id == org_id,
                KnowledgeBaseItem.id == item_id,
            )
        ).first()

    def list_items(
        self,
        org_id: UUID,
        category: Optional[str] = None,
        is_published: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[KnowledgeBaseItem], int]:
        """List knowledge base items with filtering"""
        query = self.db.query(KnowledgeBaseItem).filter(
            KnowledgeBaseItem.organization_id == org_id
        )

        if category:
            query = query.filter(KnowledgeBaseItem.category == category)

        if is_published is not None:
            query = query.filter(KnowledgeBaseItem.is_published == is_published)

        if tags:
            query = query.filter(
                KnowledgeBaseItem.tags.icontains(str(tags))  # Simple check
            )

        total = query.count()
        items = query.order_by(desc(KnowledgeBaseItem.created_at)).offset(skip).limit(limit).all()

        return items, total

    def search_items(
        self,
        org_id: UUID,
        search_query: str,
        is_published: bool = True,
        limit: int = 20,
    ) -> List[KnowledgeBaseItem]:
        """Search knowledge base items by title/content"""
        return self.db.query(KnowledgeBaseItem).filter(
            and_(
                KnowledgeBaseItem.organization_id == org_id,
                KnowledgeBaseItem.is_published == is_published,
                or_(
                    KnowledgeBaseItem.title.ilike(f"%{search_query}%"),
                    KnowledgeBaseItem.content.ilike(f"%{search_query}%"),
                ),
            )
        ).limit(limit).all()

    def update_item(
        self,
        org_id: UUID,
        item_id: UUID,
        data: KnowledgeBaseItemUpdate,
    ) -> Optional[KnowledgeBaseItem]:
        """Update a knowledge base item"""
        item = self.get_item(org_id, item_id)
        if not item:
            return None

        if data.title:
            item.title = data.title
        if data.content:
            item.content = data.content
        if data.category:
            item.category = data.category
        if data.tags is not None:
            item.tags = data.tags
        if data.is_published is not None:
            item.is_published = data.is_published
        if data.order is not None:
            item.order = data.order

        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        logger.info(f"Updated KB item {item_id}")
        return item

    def delete_item(self, org_id: UUID, item_id: UUID) -> bool:
        """Delete a knowledge base item"""
        item = self.get_item(org_id, item_id)
        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        logger.info(f"Deleted KB item {item_id}")
        return True

    def get_categories(self, org_id: UUID) -> List[str]:
        """Get all unique categories"""
        categories = self.db.query(KnowledgeBaseItem.category).filter(
            and_(
                KnowledgeBaseItem.organization_id == org_id,
                KnowledgeBaseItem.is_published == True,
            )
        ).distinct().all()
        return [c[0] for c in categories if c[0]]

    def get_tags(self, org_id: UUID) -> List[str]:
        """Get all unique tags"""
        items = self.db.query(KnowledgeBaseItem.tags).filter(
            and_(
                KnowledgeBaseItem.organization_id == org_id,
                KnowledgeBaseItem.is_published == True,
            )
        ).all()

        all_tags = set()
        for item_tags in items:
            if item_tags[0]:
                all_tags.update(item_tags[0])
        return sorted(list(all_tags))


# ============================================================================
# VECTOR EMBEDDINGS & RAG
# ============================================================================

class EmbeddingManager:
    """Manages document embeddings and vector search"""

    def __init__(self, db: Session, provider: str = "openai"):
        self.db = db
        self.provider = provider
        self.embedding_dim = 1536 if provider == "openai" else 768

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (placeholder - implement with actual API)"""
        # This would call OpenAI, Anthropic, or other embedding service
        # For now, return a placeholder vector
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        import random
        random.seed(hash_val)
        return [random.uniform(-1, 1) for _ in range(self.embedding_dim)]

    def create_embeddings_for_item(self, item: KnowledgeBaseItem) -> Dict[str, Any]:
        """Create embeddings for a KB item"""
        # Title embedding
        title_embedding = self.generate_embedding(item.title)

        # Content chunks and embeddings
        chunks = self._chunk_text(item.content, chunk_size=500)
        chunk_embeddings = [self.generate_embedding(chunk) for chunk in chunks]

        return {
            "item_id": str(item.id),
            "title_embedding": title_embedding,
            "content_chunks": chunks,
            "chunk_embeddings": chunk_embeddings,
        }

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks"""
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(" ".join(current_chunk)) >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


class RAGRetriever:
    """Retrieves relevant documents for RAG"""

    def __init__(self, db: Session, kb_manager: KnowledgeBaseManager):
        self.db = db
        self.kb_manager = kb_manager

    def retrieve_context(
        self,
        org_id: UUID,
        query: str,
        max_results: int = 5,
        similarity_threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant KB items for a query"""
        # Search for matching documents
        search_results = self.kb_manager.search_items(
            org_id,
            query,
            is_published=True,
            limit=max_results * 2,  # Get more to filter
        )

        # Score and rank results
        scored_results = []
        for item in search_results:
            score = self._calculate_relevance_score(query, item)
            if score >= similarity_threshold:
                scored_results.append({
                    "item_id": str(item.id),
                    "title": item.title,
                    "content": item.content[:500],  # Snippet
                    "category": item.category,
                    "score": score,
                })

        # Sort by score and return top results
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:max_results]

    def _calculate_relevance_score(self, query: str, item: KnowledgeBaseItem) -> float:
        """Calculate relevance score (simple implementation)"""
        query_words = set(query.lower().split())
        title_words = set(item.title.lower().split())
        content_words = set(item.content.lower().split())

        title_matches = len(query_words & title_words)
        content_matches = len(query_words & content_words)

        # Weighted scoring
        score = (title_matches * 0.7 + content_matches * 0.3) / len(query_words)
        return min(score, 1.0)  # Cap at 1.0


# ============================================================================
# DOCUMENT PROCESSING
# ============================================================================

class DocumentProcessor:
    """Processes documents for KB ingestion"""

    @staticmethod
    def process_text(text: str, title: str = None) -> Dict[str, Any]:
        """Process plain text document"""
        return {
            "title": title or "Untitled",
            "content": text,
            "word_count": len(text.split()),
            "char_count": len(text),
        }

    @staticmethod
    def process_json(json_str: str) -> Dict[str, Any]:
        """Process JSON document"""
        try:
            data = json.loads(json_str)
            return {
                "title": data.get("title", "JSON Document"),
                "content": json.dumps(data, indent=2),
                "metadata": data.get("metadata", {}),
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise

    @staticmethod
    def extract_metadata(text: str) -> Dict[str, Any]:
        """Extract metadata from document"""
        lines = text.split("\n")
        metadata = {}

        # Try to extract title from first line
        if lines:
            metadata["title"] = lines[0].strip()

        # Look for common metadata patterns
        for line in lines[:10]:
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip()

        return metadata


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

class KBBatchOperations:
    """Batch operations for knowledge base"""

    def __init__(self, db: Session, kb_manager: KnowledgeBaseManager):
        self.db = db
        self.kb_manager = kb_manager

    def bulk_create_items(
        self,
        org_id: UUID,
        user_id: UUID,
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Bulk create KB items"""
        created = []
        errors = []

        for idx, item_data in enumerate(items):
            try:
                create_schema = KnowledgeBaseItemCreate(
                    title=item_data.get("title"),
                    content=item_data.get("content"),
                    category=item_data.get("category"),
                    tags=item_data.get("tags", []),
                    is_published=item_data.get("is_published", False),
                )
                item = self.kb_manager.create_item(org_id, user_id, create_schema)
                created.append({
                    "id": str(item.id),
                    "title": item.title,
                    "status": "created",
                })
            except Exception as e:
                errors.append({
                    "index": idx,
                    "title": item_data.get("title"),
                    "error": str(e),
                })
                logger.error(f"Error creating KB item at index {idx}: {e}")

        return {
            "created_count": len(created),
            "error_count": len(errors),
            "created_items": created,
            "errors": errors,
        }

    def bulk_publish_items(
        self,
        org_id: UUID,
        item_ids: List[UUID],
    ) -> Dict[str, Any]:
        """Bulk publish KB items"""
        updated = []
        errors = []

        for item_id in item_ids:
            try:
                item = self.kb_manager.get_item(org_id, item_id)
                if not item:
                    errors.append({
                        "id": str(item_id),
                        "error": "Item not found",
                    })
                    continue

                item.is_published = True
                item.updated_at = datetime.utcnow()
                self.db.commit()
                updated.append({
                    "id": str(item.id),
                    "title": item.title,
                    "status": "published",
                })
            except Exception as e:
                errors.append({
                    "id": str(item_id),
                    "error": str(e),
                })
                logger.error(f"Error publishing KB item {item_id}: {e}")

        return {
            "updated_count": len(updated),
            "error_count": len(errors),
            "updated_items": updated,
            "errors": errors,
        }
