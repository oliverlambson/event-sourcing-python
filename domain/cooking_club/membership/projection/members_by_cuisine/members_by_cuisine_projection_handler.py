from typing import cast
from common.projection.projection_handler import ProjectionHandler
from common.event.event import Event
from domain.cooking_club.membership.event.application_submitted import ApplicationSubmitted
from domain.cooking_club.membership.event.application_evaluated import ApplicationEvaluated
from domain.cooking_club.membership.aggregate.membership import MembershipStatus
from domain.cooking_club.membership.projection.members_by_cuisine.membership_application import MembershipApplication
from domain.cooking_club.membership.projection.members_by_cuisine.membership_application_repository import MembershipApplicationRepository
from domain.cooking_club.membership.projection.members_by_cuisine.cuisine_repository import CuisineRepository
from domain.cooking_club.membership.projection.members_by_cuisine.cuisine import Cuisine

class MembersByCuisineProjectionHandler(ProjectionHandler):
    def __init__(
        self,
        cuisine_repository: CuisineRepository,
        membership_application_repository: MembershipApplicationRepository,
    ):
        self._cuisine_repository = cuisine_repository
        self._membership_application_repository = membership_application_repository

    async def project(self, event: Event) -> None:
        if isinstance(event, ApplicationSubmitted):
            await self._handle_application_submitted(event)
        elif isinstance(event, ApplicationEvaluated):
            await self._handle_application_evaluated(event)

    async def _handle_application_submitted(self, event: ApplicationSubmitted) -> None:
        await self._membership_application_repository.save(
            MembershipApplication(
                _id=event.aggregate_id,
                first_name=event.first_name,
                last_name=event.last_name,
                favorite_cuisine=event.favorite_cuisine
            )
        )

    async def _handle_application_evaluated(self, event: ApplicationEvaluated) -> None:
        if event.evaluation_outcome != MembershipStatus.APPROVED:
            return

        membership_application = await self._membership_application_repository.find_one_by_id(event.aggregate_id)
        if not membership_application:
            raise ValueError('Membership application not found')

        cuisine = await self._cuisine_repository.find_one_by_id(membership_application.favorite_cuisine)
        if not cuisine:
            cuisine = Cuisine(
                _id=membership_application.favorite_cuisine,
                member_names=[]
            )

        member_name = f"{membership_application.first_name} {membership_application.last_name}"
        cuisine.member_names.append(member_name)

        await self._cuisine_repository.save(cuisine)