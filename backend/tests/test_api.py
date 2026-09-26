"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.models import Document, Change, ChangeStatus, ChangeSource, DocumentType


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


class TestDocumentsAPI:
    """Tests for Documents API"""
    
    def test_list_documents_empty(self, client: TestClient):
        """Test listing empty documents"""
        response = client.get("/api/documents/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
    
    def test_create_document(self, client: TestClient, db):
        """Test creating a document"""
        document_data = {
            "title": "Test Document",
            "description": "Test description",
            "document_type": "ЭТрН",
            "regulations": "Test regulations",
            "source_name": "ФНС",
            "keywords": "test,keywords"
        }
        response = client.post("/api/documents/", json=document_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Document"
        assert data["id"] is not None
    
    def test_get_document(self, client: TestClient, db):
        """Test getting a specific document"""
        # First create a document
        doc = Document(
            title="Test Doc",
            document_type=DocumentType.ETN,
            regulations="Test",
            source_name="ФНС"
        )
        db.add(doc)
        db.commit()
        
        # Now get it
        response = client.get(f"/api/documents/{doc.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Doc"
    
    def test_update_document(self, client: TestClient, db):
        """Test updating a document"""
        # Create a document
        doc = Document(
            title="Test Doc",
            document_type=DocumentType.ETN,
            regulations="Test",
            source_name="ФНС"
        )
        db.add(doc)
        db.commit()
        
        # Update it
        update_data = {"title": "Updated Doc"}
        response = client.patch(f"/api/documents/{doc.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Doc"


class TestChangesAPI:
    """Tests for Changes API"""
    
    def test_list_changes_empty(self, client: TestClient):
        """Test listing empty changes"""
        response = client.get("/api/changes/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
    
    def test_create_change(self, client: TestClient):
        """Test creating a change"""
        change_data = {
            "title": "Test Change",
            "description": "Test change description",
            "source": "ФНС",
            "affected_document_types": "ЭТрН,ЭПЛ"
        }
        response = client.post("/api/changes/", json=change_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Change"
        assert data["status"] == "new"
        assert data["is_analyzed"] == False
    
    def test_mark_change_analyzed(self, client: TestClient, db):
        """Test marking a change as analyzed"""
        # Create a change
        change = Change(
            title="Test",
            description="Test",
            source=ChangeSource.FNS,
            status=ChangeStatus.NEW
        )
        db.add(change)
        db.commit()
        
        # Mark as analyzed
        response = client.get(f"/api/changes/{change.id}/mark-analyzed")
        assert response.status_code == 200
        data = response.json()
        assert data["is_analyzed"] == True
        assert data["status"] == "analyzed"


class TestNotificationsAPI:
    """Tests for Notifications API"""
    
    def test_list_notifications_empty(self, client: TestClient):
        """Test listing empty notifications"""
        response = client.get("/api/notifications/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
