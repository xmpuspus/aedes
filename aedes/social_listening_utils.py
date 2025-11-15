"""
Social Listening Utilities Module
Provides functions for collecting Google search trends data related to disease outbreaks.
"""

import logging
from typing import Optional, List
import pandas as pd

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_geo_tag(geo_tag: str) -> bool:
    """
    Validate ISO 3166-2 geo tag format.

    Args:
        geo_tag: ISO geo tag (e.g., 'PH-00', 'US-CA')

    Returns:
        bool: True if valid format

    Raises:
        ValueError: If geo tag format is invalid
    """
    import re

    if not geo_tag or not isinstance(geo_tag, str):
        raise ValueError("Geo tag must be a non-empty string")

    # Basic format check: XX-YY where XX is 2 letters, YY is 2 alphanumeric
    if not re.match(r'^[A-Z]{2}-[A-Z0-9]{2,3}$', geo_tag):
        raise ValueError(
            f"Invalid geo tag format: '{geo_tag}'. "
            "Expected format: 'XX-YY' (e.g., 'PH-00', 'US-CA'). "
            "See https://en.wikipedia.org/wiki/ISO_3166-2"
        )

    return True


def get_search_trends(
    geo_tag: str,
    keywords: Optional[List[str]] = None,
    timeframe: str = 'today 3-m'
) -> pd.DataFrame:
    """
    Get Google search trends data for dengue-related queries.

    By default, searches for 'dengue' and automatically finds top related queries.

    Args:
        geo_tag: ISO 3166-2 location code
                 PH-00 for Metro Manila
                 PH-14 for ARMM
                 See: https://en.wikipedia.org/wiki/ISO_3166-2:PH
        keywords: Optional list of keywords to search. If None, uses ['dengue']
        timeframe: Time range for search (e.g., 'today 3-m', 'today 12-m', 'all')

    Returns:
        DataFrame with search trend data over time

    Raises:
        ImportError: If pytrends is not installed
        ValueError: If geo_tag is invalid
        Exception: If API request fails

    Example:
        >>> df = get_search_trends('PH-00')
        >>> print(df.head())
    """
    try:
        # Check if pytrends is available
        if not PYTRENDS_AVAILABLE:
            raise ImportError(
                "pytrends package is required for social listening. "
                "Install it with: pip install pytrends"
            )

        logger.info(f"Fetching search trends for {geo_tag}...")

        # Validate geo tag
        validate_geo_tag(geo_tag)

        # Initialize pytrends
        pytrend = TrendReq(hl='en-US', tz=360, timeout=(10, 25))

        # Default to dengue if no keywords provided
        if keywords is None:
            keywords = ['dengue']

        # Build initial payload with primary keyword
        logger.info(f"Building payload with keywords: {keywords}")
        pytrend.build_payload(
            kw_list=[keywords[0]],
            geo=geo_tag,
            timeframe=timeframe
        )

        # Get related queries to expand search
        logger.info("Fetching related queries...")
        related_queries = pytrend.related_queries()

        # Extract top related queries
        top_queries = []
        if keywords[0] in related_queries and related_queries[keywords[0]]['top'] is not None:
            top_related = related_queries[keywords[0]]['top']
            if not top_related.empty:
                top_queries = top_related.head(4)['query'].values.tolist()
                logger.info(f"Found top related queries: {top_queries}")

        # Build final keyword list
        all_keywords = keywords + top_queries
        # Limit to 5 keywords (Google Trends API limit)
        all_keywords = all_keywords[:5]

        logger.info(f"Fetching trends for: {all_keywords}")

        # Build payload with all keywords
        pytrend.build_payload(
            kw_list=all_keywords,
            geo=geo_tag,
            timeframe=timeframe
        )

        # Get historical interest over time
        historical_search_df = pytrend.interest_over_time()

        if historical_search_df.empty:
            logger.warning(f"No trend data found for {geo_tag}")
            return pd.DataFrame()

        logger.info(f"✓ Retrieved {len(historical_search_df)} data points")

        return historical_search_df

    except ImportError as e:
        logger.error(f"Import error: {e}")
        raise

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise

    except Exception as e:
        logger.error(f"Failed to get search trends: {e}")
        raise


def get_interest_by_region(
    keyword: str,
    geo_tag: str = '',
    resolution: str = 'COUNTRY'
) -> pd.DataFrame:
    """
    Get search interest broken down by region.

    Args:
        keyword: Search keyword
        geo_tag: ISO location code (optional)
        resolution: Geographic resolution ('COUNTRY', 'REGION', 'CITY', 'DMA')

    Returns:
        DataFrame with interest by region

    Raises:
        ImportError: If pytrends is not installed
        Exception: If API request fails
    """
    try:
        if not PYTRENDS_AVAILABLE:
            raise ImportError("pytrends package is required")

        logger.info(f"Fetching interest by region for '{keyword}'...")

        pytrend = TrendReq(hl='en-US', tz=360, timeout=(10, 25))

        pytrend.build_payload([keyword], geo=geo_tag)

        interest_by_region_df = pytrend.interest_by_region(
            resolution=resolution,
            inc_low_vol=True,
            inc_geo_code=True
        )

        logger.info(f"✓ Retrieved data for {len(interest_by_region_df)} regions")

        return interest_by_region_df

    except Exception as e:
        logger.error(f"Failed to get interest by region: {e}")
        raise


def get_trending_searches(geo_tag: str = 'philippines') -> pd.DataFrame:
    """
    Get currently trending searches for a location.

    Args:
        geo_tag: Location name (e.g., 'philippines', 'united_states')

    Returns:
        DataFrame with trending searches

    Raises:
        ImportError: If pytrends is not installed
        Exception: If API request fails
    """
    try:
        if not PYTRENDS_AVAILABLE:
            raise ImportError("pytrends package is required")

        logger.info(f"Fetching trending searches for {geo_tag}...")

        pytrend = TrendReq(hl='en-US', tz=360, timeout=(10, 25))

        trending_searches_df = pytrend.trending_searches(pn=geo_tag)

        logger.info(f"✓ Retrieved {len(trending_searches_df)} trending searches")

        return trending_searches_df

    except Exception as e:
        logger.error(f"Failed to get trending searches: {e}")
        raise
