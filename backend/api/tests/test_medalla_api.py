from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.recompensa import Medalla


class MedallaAPITest(APITestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.admin = UserModel.objects.create_user(
            username="admin_medallas_api",
            password="admin-pass-123",
            email="admin_medallas_api@example.com",
            nombre="Admin Medallas API",
            is_staff=True,
        )
        self.user = UserModel.objects.create_user(
            username="user_medallas_api",
            password="user-pass-123",
            email="user_medallas_api@example.com",
            nombre="User Medallas API",
        )

        self.medalla = Medalla.objects.create(
            nombre="Medalla Inicial API",
            categoria=Medalla.CategoriaMedalla.BRONCE,
            imagen="https://example.com/bronze.png",
        )

    def test_listar_medallas_requires_active_user(self):
        url = reverse("listar-medallas")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_listar_medallas_returns_items(self):
        url = reverse("listar-medallas")
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["page"], 1)
        self.assertEqual(response.data["page_size"], 10)
        self.assertEqual(response.data["total"], 1)

    def test_listar_medallas_filters_orders_and_paginates(self):
        Medalla.objects.bulk_create([
            Medalla(nombre=f"Medalla {index:02d}", categoria=Medalla.CategoriaMedalla.ORO)
            for index in range(11)
        ])
        url = reverse("listar-medallas")
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url, {"search": "Medalla 0", "ordering": "-nombre"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 10)
        self.assertEqual(response.data["total_pages"], 1)
        self.assertEqual(response.data["items"][0]["nombre"], "Medalla 09")

        response = self.client.get(url, {"categoria": "oro", "page": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 11)
        self.assertEqual(response.data["total_pages"], 2)
        self.assertEqual(len(response.data["items"]), 1)

    def test_get_medalla_returns_404_when_missing(self):
        url = reverse("get-medalla", args=[9999])
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_medalla_returns_item(self):
        url = reverse("get-medalla", args=[self.medalla.id])
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "Medalla Inicial API")

    def test_crear_medalla_admin_requires_staff(self):
        url = reverse("crear-medalla-admin")
        payload = {
            "nombre": "Nueva API",
            "categoria": Medalla.CategoriaMedalla.ORO,
            "imagen": "https://example.com/gold.png",
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crear_medalla_admin_creates_medalla(self):
        url = reverse("crear-medalla-admin")
        payload = {
            "nombre": "Nueva API",
            "categoria": Medalla.CategoriaMedalla.ORO,
            "imagen": "https://example.com/gold.png",
        }
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Medalla.objects.filter(nombre="Nueva API").exists())

    def test_editar_medalla_admin_updates_medalla(self):
        url = reverse("editar-medalla-admin", args=[self.medalla.id])
        payload = {
            "nombre": "Medalla API Actualizada",
            "categoria": Medalla.CategoriaMedalla.PLATA,
            "imagen": "https://example.com/silver.png",
        }
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.medalla.refresh_from_db()
        self.assertEqual(self.medalla.nombre, "Medalla API Actualizada")
        self.assertEqual(self.medalla.categoria, Medalla.CategoriaMedalla.PLATA)

    def test_editar_medalla_admin_returns_404_when_missing(self):
        url = reverse("editar-medalla-admin", args=[9999])
        payload = {
            "nombre": "Medalla API Actualizada",
            "categoria": Medalla.CategoriaMedalla.PLATA,
            "imagen": "https://example.com/silver.png",
        }
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_eliminar_medalla_admin_requires_staff(self):
        url = reverse("eliminar-medalla-admin", args=[self.medalla.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_eliminar_medalla_admin_deletes_medalla(self):
        url = reverse("eliminar-medalla-admin", args=[self.medalla.id])
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Medalla.objects.filter(id=self.medalla.id).exists())

    def test_eliminar_medalla_admin_returns_404_when_missing(self):
        url = reverse("eliminar-medalla-admin", args=[9999])
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
