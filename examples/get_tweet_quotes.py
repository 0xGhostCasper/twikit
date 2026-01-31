"""
Example: Get all tweets that quote a specific tweet.

This demonstrates the new get_tweet_quotes method which uses
Twitter's search with `quoted_tweet_id:{id}` query internally.
"""

import asyncio

from twikit import Client


async def main():
    # Initialize client
    client = Client('en-US')

    # Load saved cookies (you must be logged in first)
    client.load_cookies('cookies.json')

    # The tweet ID you want to get quotes for
    tweet_id = '1234567890123456789'  # Replace with actual tweet ID

    # Method 1: Using client.get_tweet_quotes()
    print(f"Fetching quotes for tweet {tweet_id}...")
    quotes = await client.get_tweet_quotes(tweet_id, count=20)

    print(f"Found {len(quotes)} quotes on first page")
    for quote in quotes:
        print(f"  - @{quote.user.screen_name}: {quote.text[:80]}...")

    # Fetch more quotes using pagination
    if quotes.next_cursor:
        print("\nFetching more quotes...")
        more_quotes = await quotes.next()
        print(f"Found {len(more_quotes)} more quotes")
        for quote in more_quotes:
            print(f"  - @{quote.user.screen_name}: {quote.text[:80]}...")

    # Method 2: Using tweet.get_quotes() on a Tweet object
    print("\n--- Using tweet.get_quotes() ---")
    tweet = await client.get_tweet_by_id(tweet_id)
    print(f"Tweet by @{tweet.user.screen_name}: {tweet.text[:80]}...")
    print(f"Quote count: {tweet.quote_count}")

    quotes = await tweet.get_quotes(count=10)
    print(f"Retrieved {len(quotes)} quotes")
    for quote in quotes:
        print(f"  - @{quote.user.screen_name}: {quote.text[:80]}...")


async def fetch_all_quotes(client: Client, tweet_id: str, max_quotes: int = 1000):
    """
    Fetch all quotes for a tweet using pagination.

    Parameters
    ----------
    client : Client
        The authenticated twikit client.
    tweet_id : str
        The ID of the tweet to get quotes for.
    max_quotes : int, default=1000
        Maximum number of quotes to retrieve.

    Returns
    -------
    list[Tweet]
        All quote tweets found.
    """
    all_quotes = []
    quotes = await client.get_tweet_quotes(tweet_id, count=20)
    all_quotes.extend(quotes)

    while quotes.next_cursor and len(all_quotes) < max_quotes:
        print(f"  Fetched {len(all_quotes)} quotes so far...")
        quotes = await quotes.next()
        all_quotes.extend(quotes)

        # Rate limit protection
        await asyncio.sleep(1)

    return all_quotes


if __name__ == '__main__':
    asyncio.run(main())
