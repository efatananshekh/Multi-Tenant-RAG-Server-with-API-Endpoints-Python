"""
Translation Module
================

Bengali to English translation for queries.
Maps Bengali terms to English equivalents.

Add new mappings to BN_TO_EN dict.
"""

from typing import Dict

# ==================
# Bengali to English Mappings
# ==================

BN_TO_EN: Dict[str, str] = {
    # Return & Refund
    "রিটার্ন": "return",
    "রিটার্ন নীতি": "return policy",
    "রিফান্ড": "refund",
    "রিফান্ড সময়": "refund time",
    "রিফান্ড নীতি": "refund policy",

    # Contact
    "ফোন": "phone",
    "ফোন নম্বর": "phone number",
    "গ্রাহক সেবা": "customer service",
    "সাপোর্ট": "support",

    # Delivery
    "ডেলিভারি": "delivery",
    "ডেলিভারি সময়": "delivery time",
    "ডেলিভারি চার্জ": "delivery charge",

    # Orders
    "অর্ডার": "order",
    "অর্ডার বাতিল": "cancel order",
    "বাতিল": "cancel",
    "অর্ডার স্ট্যাটাস": "order status",

    # Warranty
    "ওয়ারেন্টি": "warranty",
    "ওয়ারেন্টি নীতি": "warranty policy",

    # Payments
    "বিকাশ": "bKash",
    "বিকাশ পেমেন্ট": "bKash payment",
    "রকেট": "Rocket",
    "পেমেন্ট": "payment",

    # Products
    "নন-রিটার্নেবল": "non returnable",
    "ওপেন বক্স": "open box",
    "প্রোডাক্ট": "product",

    # Accounts
    "অ্যাকাউন্ট": "account",
    "লগইন": "login",
    "পাসওয়ার্ড": "password",

    # Shipping
    "শিপিং": "shipping",
    "শিপিং চার্জ": "shipping charge",

    # General
    "হেল্প": "help",
    "যোগাযোগ": "contact",
    "কিভাবে": "how to",
}


def is_bengali(text: str) -> bool:
    """
    Check if text contains Bengali characters.

    Args:
        text: Text to check

    Returns:
        True if text contains Bengali (non-ASCII > 127)
    """
    return any(ord(c) > 127 for c in text)


def translate_query(query_text: str) -> str:
    """
    Translate Bengali query to English.

    Args:
        query_text: The query text (may contain Bengali)

    Returns:
        English translation if found, original text otherwise
    """
    if not is_bengali(query_text):
        return query_text

    # Try exact match first
    q_lower = query_text.lower().strip()
    if q_lower in BN_TO_EN:
        return BN_TO_EN[q_lower]

    # Partial match - check each word
    words = query_text.split()
    translated_words = []

    for word in words:
        word_lower = word.lower()
        if word_lower in BN_TO_EN:
            translated_words.append(BN_TO_EN[word_lower])
        else:
            translated_words.append(word)

    if translated_words != words:
        return " ".join(translated_words)

    return query_text


def get_all_mappings() -> Dict[str, str]:
    """Return all Bengali to English mappings."""
    return BN_TO_EN.copy()


def add_mapping(bengali: str, english: str) -> None:
    """Add a new mapping."""
    BN_TO_EN[bengali.lower()] = english.lower()


def remove_mapping(bengali: str) -> bool:
    """Remove a mapping."""
    if bengali.lower() in BN_TO_EN:
        del BN_TO_EN[bengali.lower()]
        return True
    return False