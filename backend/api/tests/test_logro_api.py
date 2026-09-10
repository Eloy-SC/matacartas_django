from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.recompensa import Logro, RequisitoLogro


class LogroAPITest(APITestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.user = UserModel.objects.create_user(
            username="user_logros_api",
            password="user-pass-123",
            email="user_logros_api@example.com",
            nombre="User Logros API",
        )
        self.logro = Logro.objects.create(
            nombre="Logro Inicial API",
            descripcion="Descripción inicial",
            oculto=False,
        )
        RequisitoLogro.objects.create(
            logro=self.logro,
            requisito=RequisitoLogro.Requisito.PARTIDAS_GANADAS,
            valor_necesario=3,
        )

    def test_listar_logros_requires_active_user(self):
        response = self.client.get(reverse("listar-logros"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_listar_logros_returns_requirements(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("listar-logros"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 1)
        self.assertEqual(response.data["items"][0]["nombre"], "Logro Inicial API")
        self.assertEqual(response.data["items"][0]["requisitos"][0]["valor_necesario"], 3)

    def test_listar_logros_filters_orders_and_paginates(self):
        Logro.objects.bulk_create(
            [
                Logro(
                    nombre=f"Logro {index:02d}",
                    descripcion="Logro filtrable",
                    oculto=True,
                )
                for index in range(11)
            ]
        )
        self.client.force_authenticate(user=self.user)
        url = reverse("listar-logros")

        response = self.client.get(url, {"search": "Logro 0", "ordering": "-nombre"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 10)
        self.assertEqual(response.data["items"][0]["nombre"], "Logro 09")

        response = self.client.get(url, {"oculto": "true", "page": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 11)
        self.assertEqual(response.data["total_pages"], 2)
        self.assertEqual(len(response.data["items"]), 1)