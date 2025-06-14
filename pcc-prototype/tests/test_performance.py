"""
Performance tests for API endpoints
"""

import asyncio
import time
import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_bed_status_performance():
    """Ensure bed status API responds quickly"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login first
        login_response = await client.post(
            "/token",
            data={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # First call - cache miss
        start = time.time()
        response = await client.get("/api/bed-status", headers=headers)
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 5.0, f"First response took {duration}s, expected <5s (cache miss)"
        
        # Second call - should hit cache
        start = time.time()
        response = await client.get("/api/bed-status", headers=headers)
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0, f"Cached response took {duration}s, expected <1s"


@pytest.mark.asyncio
async def test_cache_effectiveness():
    """Verify cache reduces response time"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/token",
            data={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make multiple calls
        timings = []
        for i in range(5):
            start = time.time()
            response = await client.get("/api/bed-status", headers=headers)
            duration = time.time() - start
            timings.append(duration)
            assert response.status_code == 200
            
        # First call should be slowest (cache miss)
        # Subsequent calls should be faster (cache hits)
        avg_cached = sum(timings[1:]) / len(timings[1:])
        assert avg_cached < timings[0] / 2, f"Cached calls not significantly faster: first={timings[0]}, avg_cached={avg_cached}"


if __name__ == "__main__":
    # Run a simple performance test
    async def main():
        print("Testing /api/bed-status performance...")
        await test_bed_status_performance()
        print("✅ Performance test passed!")
        
    asyncio.run(main())