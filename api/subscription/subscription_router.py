import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

from config.subscription_stripe_settings import subscription_settings

stripe.api_key = subscription_settings.STRIPE_ID

router = APIRouter()

class SubscriptionRequest(BaseModel):
    subscriptionType: Literal["Premium", "Enterprise"] = Field(...)

class SubscriptionResponse(BaseModel):
    stripeUrl: str

@router.post("/subscription", response_model=SubscriptionResponse)
def create_subscription(request: SubscriptionRequest):
    price_mapping = {
        "Premium": subscription_settings.PRICE_ID_PREMIUM,
        "Enterprise": subscription_settings.PRICE_ID_ENTERPRISE
    }

    if request.subscriptionType not in price_mapping:
        raise HTTPException(status_code=400, detail="Invalid subscription type.")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_mapping[request.subscriptionType],
                "quantity": 1,
            }],
            mode="subscription",
            success_url="https://cbts-frontend.vercel.app/subscription/success",
            cancel_url="https://cbts-frontend.vercel.app/subscription/cancel",
        )

        return SubscriptionResponse(stripeUrl=session.url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
