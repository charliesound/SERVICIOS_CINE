import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy import select, update
from database import AsyncSessionLocal
from models.core import Project
from models.delivery import Deliverable
from models.review import Review, ApprovalDecision, ReviewComment


async def patch_data():
    print("Starting data patching for multi-tenant isolation...")
    async with AsyncSessionLocal() as db:
        async with db.begin():
            # 1. Patch Reviews
            print("Patching Reviews...")
            reviews_result = await db.execute(
                select(Review).where(Review.organization_id == None)
            )
            reviews = reviews_result.scalars().all()
            for review in reviews:
                project_result = await db.execute(
                    select(Project).where(Project.id == review.project_id)
                )
                project = project_result.scalar_one_or_none()
                if project:
                    review.organization_id = project.organization_id
                    print(
                        f"Patched Review {review.id} with Org {project.organization_id}"
                    )
                else:
                    print(
                        f"Warning: Project {review.project_id} not found for Review {review.id}"
                    )

            # 2. Patch Deliverables
            print("Patching Deliverables...")
            deliverables_result = await db.execute(
                select(Deliverable).where(Deliverable.organization_id == None)
            )
            deliverables = deliverables_result.scalars().all()
            for deliverable in deliverables:
                project_result = await db.execute(
                    select(Project).where(Project.id == deliverable.project_id)
                )
                project = project_result.scalar_one_or_none()
                if project:
                    deliverable.organization_id = project.organization_id
                    print(
                        f"Patched Deliverable {deliverable.id} with Org {project.organization_id}"
                    )
                else:
                    print(
                        f"Warning: Project {deliverable.project_id} not found for Deliverable {deliverable.id}"
                    )

            # 3. Patch ApprovalDecisions
            print("Patching ApprovalDecisions...")
            decisions_result = await db.execute(
                select(ApprovalDecision).where(ApprovalDecision.organization_id == None)
            )
            decisions = decisions_result.scalars().all()
            for decision in decisions:
                review_result = await db.execute(
                    select(Review).where(Review.id == decision.review_id)
                )
                review = review_result.scalar_one_or_none()
                if review and review.organization_id:
                    decision.organization_id = review.organization_id
                    print(
                        f"Patched ApprovalDecision {decision.id} from Review {review.id}"
                    )
                elif review:
                    print(
                        f"Warning: Review {review.id} has no organization_id yet for Decision {decision.id}"
                    )
                else:
                    print(
                        f"Warning: Review {decision.review_id} not found for Decision {decision.id}"
                    )

            # 4. Patch ReviewComments
            print("Patching ReviewComments...")
            comments_result = await db.execute(
                select(ReviewComment).where(ReviewComment.organization_id == None)
            )
            comments = comments_result.scalars().all()
            for comment in comments:
                # Look up the parent Review to get organization_id
                review_lookup = await db.execute(
                    select(Review).where(Review.id == comment.review_id)
                )
                review = review_lookup.scalar_one_or_none()
                if review and review.organization_id:
                    comment.organization_id = review.organization_id
                    print(f"Patched ReviewComment {comment.id} from Review {review.id}")
                elif review:
                    print(
                        f"Warning: Review {review.id} has no organization_id yet for Comment {comment.id}"
                    )
                else:
                    print(
                        f"Warning: Review {comment.review_id} not found for Comment {comment.id}"
                    )

            await db.commit()
    print("Data patching complete.")


if __name__ == "__main__":
    asyncio.run(patch_data())
