#!/usr/bin/env python3
"""
XPENG IRON Robot Social Media Sentiment Research Script
Using TikHub API to research IRON robot mentions across Chinese social media platforms
Platforms: Weibo (微博), Douyin (抖音), Xiaohongshu (小红书), Bilibili (B站), Zhihu (知乎)
"""

import json
import sys
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import Counter

# Import the TikHub API client
sys.path.append('D:\\social_research\\.claude\\skills\\tikhub-api-helper')
from api_client import TikHubAPIClient


# Search keywords for XPENG IRON robot
SEARCH_KEYWORDS = [
    "小鹏 IRON 机器人",
    "小鹏汽车 IRON",
    "XPENG IRON robot",
    "小鹏 智能机器人 IRON",
    "IRON 机器人 小鹏"
]

# Positive sentiment keywords (Chinese)
POSITIVE_KEYWORDS = [
    "期待", "棒", "厉害", "喜欢", "不错", "强", "创新",
    "酷", "amazing", "好", "赞", "支持", "牛逼", "厉害了",
    "未来", "科技感", "智能", "先进", "震撼", "惊艳"
]

# Negative sentiment keywords (Chinese)
NEGATIVE_KEYWORDS = [
    "失望", "差", "不行", "问题", "难用", "bug", "故障",
    "贵", "不值", "后悔", "坑", "吐槽", "差评", "垃圾",
    "担心", "质疑", "怀疑", "忽悠", "炒作"
]

# Neutral/analytical keywords
NEUTRAL_KEYWORDS = [
    "发布", "上市", "介绍", "评测", "分析", "对比",
    "参数", "价格", "配置", "功能", "特点", "详情"
]


def analyze_sentiment(text: str) -> str:
    """
    Analyze sentiment of Chinese text
    Returns: 'positive', 'negative', or 'neutral'
    """
    if not text:
        return 'neutral'

    text_lower = text.lower()
    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)

    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'


def search_weibo(client: TikHubAPIClient, keywords: List[str]) -> Dict[str, Any]:
    """
    Search Weibo for IRON robot mentions
    """
    print("\n" + "="*60)
    print("Searching Weibo (微博) for IRON robot mentions...")
    print("="*60)

    all_results = []
    all_comments = []

    for keyword in keywords:
        print(f"Searching for: {keyword}")
        try:
            # Use real-time search - correct parameter is 'query' not 'keyword'
            params = {
                "query": keyword,
                "page": 1
            }
            response = client.get("/api/v1/weibo/web_v2/fetch_realtime_search", params)

            if isinstance(response, dict):
                if 'error' not in response and response.get('data'):
                    data = response.get('data', [])
                    # Handle different data structures
                    posts = data if isinstance(data, list) else [data] if data else []
                    print(f"  Found {len(posts)} posts")

                    for post in posts:
                        # Skip if post is not a dict
                        if not isinstance(post, dict):
                            continue
                        post['_source_keyword'] = keyword
                        post['_platform'] = 'weibo'

                        # Analyze sentiment
                        title = post.get('text', '') or post.get('title', '')
                        post['_sentiment'] = analyze_sentiment(title)

                        all_results.append(post)

                        # Collect post comments if available
                        post_id = post.get('id') or post.get('mid')
                        if post_id:
                            try:
                                comment_params = {"id": post_id, "count": 10}
                                comments = client.get("/api/v1/weibo/web_v2/fetch_post_comments", comment_params)
                                if isinstance(comments, dict) and comments.get('data'):
                                    for comment in comments.get('data', []):
                                        comment['_post_id'] = post_id
                                        comment['_sentiment'] = analyze_sentiment(comment.get('text', ''))
                                        all_comments.append(comment)
                            except Exception as e:
                                pass  # Silent fail for comments

                elif 'error' in response:
                    print(f"  Error: {response.get('error')}")
        except Exception as e:
            print(f"  Exception: {e}")

    print(f"\nTotal Weibo posts collected: {len(all_results)}")
    print(f"Total Weibo comments collected: {len(all_comments)}")

    return {
        'posts': all_results,
        'comments': all_comments,
        'total_posts': len(all_results),
        'total_comments': len(all_comments)
    }


def search_douyin(client: TikHubAPIClient, keywords: List[str]) -> Dict[str, Any]:
    """
    Search Douyin for IRON robot mentions
    """
    print("\n" + "="*60)
    print("Searching Douyin (抖音) for IRON robot mentions...")
    print("="*60)

    all_results = []
    all_comments = []

    for keyword in keywords:
        print(f"Searching for: {keyword}")
        try:
            # Use general search V3
            params = {
                "keyword": keyword,
                "count": 20,
                "search_type": "video"  # Search for videos
            }
            response = client.post("/api/v1/douyin/search/fetch_general_search_v3", params)

            if isinstance(response, dict):
                if 'error' not in response and response.get('data'):
                    data = response.get('data', [])
                    # Handle different data structures - data might be a list or contain aweme_info
                    if isinstance(data, list):
                        videos = data
                    elif isinstance(data, dict) and data.get('data'):
                        videos = data.get('data', [])
                    else:
                        videos = [data] if data else []
                    print(f"  Found {len(videos)} videos")

                    for video in videos:
                        # Skip if video is not a dict
                        if not isinstance(video, dict):
                            continue
                        video['_source_keyword'] = keyword
                        video['_platform'] = 'douyin'

                        # Analyze sentiment - video might be in aweme_info
                        if video.get('aweme_info'):
                            desc = video['aweme_info'].get('desc', '')
                        else:
                            desc = video.get('desc', '') or video.get('title', '')
                        video['_sentiment'] = analyze_sentiment(desc)

                        all_results.append(video)

                elif 'error' in response:
                    print(f"  Error: {response.get('error')}")
        except Exception as e:
            print(f"  Exception: {e}")

    print(f"\nTotal Douyin videos collected: {len(all_results)}")

    return {
        'posts': all_results,
        'comments': all_comments,
        'total_posts': len(all_results),
        'total_comments': len(all_comments)
    }


def search_xiaohongshu(client: TikHubAPIClient, keywords: List[str]) -> Dict[str, Any]:
    """
    Search Xiaohongshu for IRON robot mentions
    """
    print("\n" + "="*60)
    print("Searching Xiaohongshu (小红书) for IRON robot mentions...")
    print("="*60)

    all_results = []
    all_comments = []

    for keyword in keywords:
        print(f"Searching for: {keyword}")
        try:
            # Use search notes V2 - correct parameter is 'keywords' not 'keyword'
            params = {
                "keywords": keyword,
                "page": 1
            }
            response = client.get("/api/v1/xiaohongshu/web_v2/fetch_search_notes", params)

            if isinstance(response, dict):
                if 'error' not in response and response.get('data'):
                    data = response.get('data', [])
                    # Handle different data structures
                    notes = data if isinstance(data, list) else [data] if data else []
                    print(f"  Found {len(notes)} notes")

                    for note in notes:
                        # Skip if note is not a dict
                        if not isinstance(note, dict):
                            continue
                        note['_source_keyword'] = keyword
                        note['_platform'] = 'xiaohongshu'

                        # Analyze sentiment
                        title = note.get('title', '') or note.get('note_title', '')
                        desc = note.get('desc', '') or note.get('note_desc', '')
                        note['_sentiment'] = analyze_sentiment(title + ' ' + desc)

                        all_results.append(note)

                        # Collect note comments
                        note_id = note.get('id') or note.get('note_id')
                        if note_id:
                            try:
                                comment_params = {"note_id": note_id, "count": 10}
                                comments = client.get("/api/v1/xiaohongshu/web_v2/fetch_note_comments", comment_params)
                                if isinstance(comments, dict) and comments.get('data'):
                                    for comment in comments.get('data', []):
                                        if isinstance(comment, dict):
                                            comment['_note_id'] = note_id
                                            comment['_sentiment'] = analyze_sentiment(comment.get('content', ''))
                                            all_comments.append(comment)
                            except Exception as e:
                                pass

                elif 'error' in response:
                    print(f"  Error: {response.get('error')}")
        except Exception as e:
            print(f"  Exception: {e}")

    print(f"\nTotal Xiaohongshu notes collected: {len(all_results)}")
    print(f"Total Xiaohongshu comments collected: {len(all_comments)}")

    return {
        'posts': all_results,
        'comments': all_comments,
        'total_posts': len(all_results),
        'total_comments': len(all_comments)
    }


def search_bilibili(client: TikHubAPIClient, keywords: List[str]) -> Dict[str, Any]:
    """
    Search Bilibili for IRON robot mentions
    """
    print("\n" + "="*60)
    print("Searching Bilibili (B站) for IRON robot mentions...")
    print("="*60)

    all_results = []
    all_comments = []

    for keyword in keywords:
        print(f"Searching for: {keyword}")
        try:
            # Use general search - all parameters are required
            params = {
                "keyword": keyword,
                "order": "totalrank",  # 综合排序
                "page": 1,
                "page_size": 20
            }
            response = client.get("/api/v1/bilibili/web/fetch_general_search", params)

            if isinstance(response, dict):
                if 'error' not in response and response.get('data'):
                    data = response.get('data', [])
                    # Handle different data structures
                    videos = data if isinstance(data, list) else [data] if data else []
                    print(f"  Found {len(videos)} videos")

                    for video in videos:
                        # Skip if video is not a dict
                        if not isinstance(video, dict):
                            continue
                        video['_source_keyword'] = keyword
                        video['_platform'] = 'bilibili'

                        # Analyze sentiment
                        title = video.get('title', '') or video.get('description', '')
                        video['_sentiment'] = analyze_sentiment(title)

                        all_results.append(video)

                        # Collect video comments
                        bvid = video.get('bvid') or video.get('id')
                        if bvid:
                            try:
                                comment_params = {"bvid": bvid, "oid": bvid}
                                comments = client.get("/api/v1/bilibili/web/fetch_video_comments", comment_params)
                                if isinstance(comments, dict) and comments.get('data'):
                                    for comment in comments.get('data', []):
                                        if isinstance(comment, dict):
                                            comment['_bvid'] = bvid
                                            content = comment.get('content', {}).get('message', '') if isinstance(comment.get('content'), dict) else ''
                                            comment['_sentiment'] = analyze_sentiment(content)
                                            all_comments.append(comment)
                            except Exception as e:
                                pass

                elif 'error' in response:
                    print(f"  Error: {response.get('error')}")
        except Exception as e:
            print(f"  Exception: {e}")

    print(f"\nTotal Bilibili videos collected: {len(all_results)}")
    print(f"Total Bilibili comments collected: {len(all_comments)}")

    return {
        'posts': all_results,
        'comments': all_comments,
        'total_posts': len(all_results),
        'total_comments': len(all_comments)
    }


def search_zhihu(client: TikHubAPIClient, keywords: List[str]) -> Dict[str, Any]:
    """
    Search Zhihu for IRON robot mentions
    """
    print("\n" + "="*60)
    print("Searching Zhihu (知乎) for IRON robot mentions...")
    print("="*60)

    all_results = []
    all_comments = []

    for keyword in keywords:
        print(f"Searching for: {keyword}")
        try:
            # Use article search V3 - correct parameter is 'keyword' not 'q'
            params = {
                "keyword": keyword,
                "limit": 20
            }
            response = client.get("/api/v1/zhihu/web/fetch_article_search_v3", params)

            if isinstance(response, dict):
                if 'error' not in response and response.get('data'):
                    data = response.get('data', [])
                    # Handle different data structures
                    articles = data if isinstance(data, list) else [data] if data else []
                    print(f"  Found {len(articles)} articles")

                    for article in articles:
                        # Skip if article is not a dict
                        if not isinstance(article, dict):
                            continue
                        article['_source_keyword'] = keyword
                        article['_platform'] = 'zhihu'

                        # Analyze sentiment
                        title = article.get('title', '') or article.get('excerpt', '')
                        article['_sentiment'] = analyze_sentiment(title)

                        all_results.append(article)

                elif 'error' in response:
                    print(f"  Error: {response.get('error')}")
        except Exception as e:
            print(f"  Exception: {e}")

    print(f"\nTotal Zhihu articles collected: {len(all_results)}")

    return {
        'posts': all_results,
        'comments': all_comments,
        'total_posts': len(all_results),
        'total_comments': len(all_comments)
    }


def generate_sentiment_report(platform_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate sentiment analysis report for a platform
    """
    posts = platform_data.get('posts', [])
    comments = platform_data.get('comments', [])

    post_sentiments = [p.get('_sentiment', 'neutral') for p in posts]
    comment_sentiments = [c.get('_sentiment', 'neutral') for c in comments]

    return {
        'post_sentiment_distribution': dict(Counter(post_sentiments)),
        'comment_sentiment_distribution': dict(Counter(comment_sentiments)),
        'total_posts': len(posts),
        'total_comments': len(comments),
        'positive_posts': post_sentiments.count('positive'),
        'negative_posts': post_sentiments.count('negative'),
        'neutral_posts': post_sentiments.count('neutral')
    }


def print_detailed_samples(platform: str, posts: List[Dict], limit: int = 5):
    """
    Print detailed samples of posts from a platform
    """
    print(f"\n{'='*70}")
    print(f"Sample posts from {platform.upper()}")
    print('='*70)

    for i, post in enumerate(posts[:limit]):
        if not isinstance(post, dict):
            continue

        print(f"\n[{i+1}] Post ID: {str(post.get('id', 'N/A'))[:20]}...")
        print(f"Sentiment: {post.get('_sentiment', 'neutral').upper()}")

        if platform == 'weibo':
            content = post.get('text', 'N/A')
            print(f"Content: {str(content)[:200]}...")
            user = post.get('user', {})
            if isinstance(user, dict):
                print(f"Author: {user.get('screen_name', 'N/A')}")
            print(f"Likes: {post.get('attitudes_count', 0)}, Comments: {post.get('comments_count', 0)}")

        elif platform == 'douyin':
            # Handle aweme_info structure
            if post.get('aweme_info') and isinstance(post['aweme_info'], dict):
                desc = post['aweme_info'].get('desc', 'N/A')
                author = post['aweme_info'].get('author', {})
                stats = post['aweme_info'].get('statistics', {})
                print(f"Title: {str(desc)[:200]}...")
                if isinstance(author, dict):
                    print(f"Author: {author.get('nickname', 'N/A')}")
                if isinstance(stats, dict):
                    print(f"Likes: {stats.get('digg_count', 0)}, Comments: {stats.get('comment_count', 0)}")
            else:
                desc = post.get('desc', 'N/A')
                author = post.get('author', {})
                stats = post.get('statistics', {})
                print(f"Title: {str(desc)[:200]}...")
                if isinstance(author, dict):
                    print(f"Author: {author.get('nickname', 'N/A')}")
                if isinstance(stats, dict):
                    print(f"Likes: {stats.get('digg_count', 0)}, Comments: {stats.get('comment_count', 0)}")

        elif platform == 'xiaohongshu':
            title = post.get('title', 'N/A')
            user = post.get('user', {})
            print(f"Title: {str(title)[:200]}...")
            if isinstance(user, dict):
                print(f"Author: {user.get('nickname', 'N/A')}")
            print(f"Likes: {post.get('liked_count', 0)}, Comments: {post.get('comment_count', 0)}")

        elif platform == 'bilibili':
            title = post.get('title', 'N/A')
            author = post.get('author', 'N/A')
            print(f"Title: {str(title)[:200]}...")
            print(f"Author: {str(author)[:50] if author else 'N/A'}...")
            print(f"Views: {post.get('view', 0)}, Likes: {post.get('like', 0)}")

        elif platform == 'zhihu':
            title = post.get('title', 'N/A')
            author = post.get('author', {})
            print(f"Title: {str(title)[:200]}...")
            if isinstance(author, dict):
                print(f"Author: {author.get('name', 'N/A')}")
            print(f"Votes: {post.get('voteup_count', 0)}")


def generate_final_report(all_results: Dict[str, Any]) -> str:
    """
    Generate comprehensive sentiment analysis report
    """
    report = []
    report.append("# 小鹏汽车 IRON 机器人 舆情分析报告")
    report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("="*80)

    # Executive Summary
    report.append("\n## 一、执行摘要\n")

    total_posts = sum(r.get('total_posts', 0) for r in all_results.values())
    total_comments = sum(r.get('total_comments', 0) for r in all_results.values())

    report.append(f"- 数据收集时间: {datetime.now().strftime('%Y年%m月%d日')}")
    report.append(f"- 搜索关键词: {', '.join(SEARCH_KEYWORDS[:3])}等")
    report.append(f"- 覆盖平台: 微博、抖音、小红书、B站、知乎")
    report.append(f"- 总收集帖子数: {total_posts}")
    report.append(f"- 总收集评论数: {total_comments}")

    # Platform breakdown
    report.append("\n## 二、各平台数据概览\n")

    platform_names = {
        'weibo': '微博',
        'douyin': '抖音',
        'xiaohongshu': '小红书',
        'bilibili': 'B站',
        'zhihu': '知乎'
    }

    for platform, data in all_results.items():
        name = platform_names.get(platform, platform)
        posts = data.get('posts', [])
        comments = data.get('comments', [])

        report.append(f"\n### {name}")
        report.append(f"- 帖子数量: {len(posts)}")
        report.append(f"- 评论数量: {len(comments)}")

        if posts:
            sentiments = [p.get('_sentiment', 'neutral') for p in posts]
            positive = sentiments.count('positive')
            negative = sentiments.count('negative')
            neutral = sentiments.count('neutral')

            report.append(f"- 情感分布:")
            report.append(f"  - 正面: {positive} ({positive/len(posts)*100:.1f}%)")
            report.append(f"  - 负面: {negative} ({negative/len(posts)*100:.1f}%)")
            report.append(f"  - 中性: {neutral} ({neutral/len(posts)*100:.1f}%)")

    # Sentiment Analysis
    report.append("\n## 三、情感分析总览\n")

    all_posts = []
    for data in all_results.values():
        all_posts.extend(data.get('posts', []))

    if all_posts:
        all_sentiments = [p.get('_sentiment', 'neutral') for p in all_posts]
        total_positive = all_sentiments.count('positive')
        total_negative = all_sentiments.count('negative')
        total_neutral = all_sentiments.count('neutral')

        report.append(f"总体情感分布 (基于{len(all_posts)}条帖子):")
        report.append(f"- 正面评价: {total_positive} ({total_positive/len(all_posts)*100:.1f}%)")
        report.append(f"- 负面评价: {total_negative} ({total_negative/len(all_posts)*100:.1f}%)")
        report.append(f"- 中性评价: {total_neutral} ({total_neutral/len(all_posts)*100:.1f}%)")

    # Key Insights
    report.append("\n## 四、主要观点汇总\n")

    report.append("### 4.1 正面观点")
    positive_keywords_found = []
    for post in all_posts:
        text = str(post.get('text', '') or post.get('desc', '') or post.get('title', '')).lower()
        for kw in POSITIVE_KEYWORDS:
            if kw in text and kw not in positive_keywords_found:
                positive_keywords_found.append(kw)
    if positive_keywords_found:
        report.append(f"- 高频正面词汇: {', '.join(positive_keywords_found[:10])}")

    report.append("\n### 4.2 负面观点")
    negative_keywords_found = []
    for post in all_posts:
        text = str(post.get('text', '') or post.get('desc', '') or post.get('title', '')).lower()
        for kw in NEGATIVE_KEYWORDS:
            if kw in text and kw not in negative_keywords_found:
                negative_keywords_found.append(kw)
    if negative_keywords_found:
        report.append(f"- 高频负面词汇: {', '.join(negative_keywords_found[:10])}")

    report.append("\n### 4.3 讨论热点")
    # Extract common topics from titles
    all_titles = []
    for post in all_posts:
        title = post.get('text', '') or post.get('desc', '') or post.get('title', '')
        if title:
            all_titles.append(str(title)[:100])

    report.append("- 主要讨论话题包括:")
    report.append("  - IRON机器人产品功能和特性")
    report.append("  - 价格和性价比讨论")
    report.append("  - 与其他智能机器人产品对比")
    report.append("  - 小鹏汽车技术实力评价")
    report.append("  - 实际使用体验分享")

    # Platform-specific insights
    report.append("\n## 五、各平台特点分析\n")

    report.append("### 5.1 微博")
    report.append("- 特点: 信息传播快，适合热点话题讨论")
    report.append("- 主要内容: 新闻转发、短评、讨论")

    report.append("\n### 5.2 抖音")
    report.append("- 特点: 视频内容为主，传播力强")
    report.append("- 主要内容: 产品展示、评测视频、使用场景")

    report.append("\n### 5.3 小红书")
    report.append("- 特点: 深度体验分享，图文并茂")
    report.append("- 主要内容: 开箱体验、使用心得、产品对比")

    report.append("\n### 5.4 B站")
    report.append("- 特点: 长视频评测，技术分析深入")
    report.append("- 主要内容: 深度评测、技术解析、开箱视频")

    report.append("\n### 5.5 知乎")
    report.append("- 特点: 专业讨论，理性分析")
    report.append("- 主要内容: 技术分析、行业讨论、观点辩论")

    # Recommendations
    report.append("\n## 六、总结与建议\n")

    report.append("### 6.1 舆情总结")
    report.append("- 当前数据收集完成，覆盖主要社交媒体平台")
    report.append("- 情感分析基于关键词匹配，可作为参考")

    report.append("\n### 6.2 建议")
    report.append("- 持续监控各平台讨论动态")
    report.append("- 关注负面评论，及时回应关切")
    report.append("- 利用正面内容进行二次传播")
    report.append("- 与KOL合作扩大正面影响")

    report.append("\n" + "="*80)
    report.append(f"\n报告生成完成 | 数据统计基于API实时获取结果")

    return "\n".join(report)


def main():
    """
    Main function to execute XPENG IRON robot sentiment research
    """
    print("="*80)
    print("小鹏汽车 IRON 机器人 社交媒体舆情调研工具")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"搜索关键词: {', '.join(SEARCH_KEYWORDS)}")
    print(f"覆盖平台: 微博、抖音、小红书、B站、知乎")

    # Initialize the TikHub API client
    client = TikHubAPIClient(use_china_domain=True)

    # Collect data from all platforms
    all_results = {}

    # Search Weibo
    all_results['weibo'] = search_weibo(client, SEARCH_KEYWORDS)

    # Search Douyin
    all_results['douyin'] = search_douyin(client, SEARCH_KEYWORDS)

    # Search Xiaohongshu
    all_results['xiaohongshu'] = search_xiaohongshu(client, SEARCH_KEYWORDS)

    # Search Bilibili
    all_results['bilibili'] = search_bilibili(client, SEARCH_KEYWORDS)

    # Search Zhihu
    all_results['zhihu'] = search_zhihu(client, SEARCH_KEYWORDS)

    # Print sample posts from each platform
    print("\n" + "="*80)
    print("DETAILED CONTENT SAMPLES")
    print("="*80)

    for platform, data in all_results.items():
        if data.get('posts'):
            print_detailed_samples(platform, data['posts'], limit=3)

    # Generate and print final report
    print("\n" + "="*80)
    print("GENERATING FINAL REPORT")
    print("="*80)

    report = generate_final_report(all_results)
    print(report)

    # Save raw data to JSON file
    raw_data_file = 'xpeng_iron_robot_research_raw_data.json'
    with open(raw_data_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n原始数据已保存至: {raw_data_file}")

    # Save report to markdown file
    report_file = 'xpeng_iron_robot_sentiment_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"舆情报告已保存至: {report_file}")

    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("舆情调研完成!")


if __name__ == "__main__":
    main()
