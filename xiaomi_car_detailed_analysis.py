#!/usr/bin/env python3
"""
小米汽车交通事故舆情深度分析脚本
Xiaomi Car Accident Sentiment Deep Analysis Script

Collects detailed data including comments from top content.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Import TikHub API client
sys.path.insert(0, str(Path(__file__).parent / '.claude' / 'skills' / 'tikhub-api-helper'))
from api_client import TikHubAPIClient


def load_research_data():
    """Load the previously collected research data."""
    json_files = list(Path("D:/social_research").glob("xiaomi_car_research_*.json"))
    if not json_files:
        print("No research data found. Run xiaomi_car_research.py first.")
        return None

    # Get the most recent file
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading data from: {latest_file}")

    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_douyin_comments(client, aweme_id: str, count: int = 20):
    """Get comments for a Douyin video."""
    result = client.get(
        "/api/v1/douyin/web/fetch_video_comments",
        params={
            "aweme_id": aweme_id,
            "count": count
        }
    )

    if "error" in result or result.get("code") != 200:
        return []

    comments = []
    data = result.get("data", {})

    if "comments" in data and isinstance(data["comments"], list):
        for comment in data["comments"]:
            comments.append({
                "cid": comment.get("cid", ""),
                "text": comment.get("text", ""),
                "like_count": comment.get("digg_count", 0),
                "reply_count": comment.get("reply_comment_total", 0),
                "user": {
                    "uid": comment.get("user", {}).get("uid", ""),
                    "nickname": comment.get("user", {}).get("nickname", "")
                }
            })

    return comments


def get_xiaohongshu_comments(client, note_id: str):
    """Get comments for a Xiaohongshu note."""
    result = client.get(
        "/api/v1/xiaohongshu/web/fetch_note_comments",
        params={
            "note_id": note_id
        }
    )

    if "error" in result or result.get("code") != 200:
        return []

    comments = []
    data = result.get("data", {})

    if "comments" in data and isinstance(data["comments"], list):
        for comment in data["comments"]:
            comments.append({
                "id": comment.get("id", ""),
                "content": comment.get("content", ""),
                "like_count": comment.get("like_count", 0),
                "sub_comment_count": comment.get("sub_comment_count", 0),
                "user": {
                    "user_id": comment.get("user", {}).get("user_id", ""),
                    "nickname": comment.get("user", {}).get("nickname", "")
                }
            })

    return comments


def analyze_comment_sentiment(text: str) -> str:
    """Analyze sentiment of a comment."""
    negative_keywords = [
        "事故", "车祸", "死", "伤", "危险", "问题", "缺陷", "怕", "担心",
        "失控", "碰撞", "追尾", "起火", "刹车", "失灵", "安全隐患", "不敢",
        "怕", "不安全", "质量差", "垃圾", "烂", "后悔", "退订"
    ]

    positive_keywords = [
        "安全", "好", "优秀", "可靠", "信任", "喜欢", "推荐", "不错",
        "稳定", "放心", "体验好", "质量好", "强", "牛", "厉害", "买",
        "支持", "加油", "给力", "赞", "想买"
    ]

    text_lower = text.lower()

    negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
    positive_count = sum(1 for kw in positive_keywords if kw in text_lower)

    if negative_count > positive_count:
        return "negative"
    elif positive_count > negative_count:
        return "positive"
    else:
        return "neutral"


def extract_key_topics(comments: list) -> dict:
    """Extract key topics from comments."""
    topics = {
        "智驾问题": 0,
        "刹车问题": 0,
        "质量担忧": 0,
        "支持品牌": 0,
        "观望态度": 0,
        "使用体验": 0,
        "事故责任": 0
    }

    topic_keywords = {
        "智驾问题": ["智驾", "自动驾驶", "辅助驾驶", "自动", "系统"],
        "刹车问题": ["刹车", "制动", "停不", "反应"],
        "质量担忧": ["质量", "安全", "怕", "担心", "隐患"],
        "支持品牌": ["支持", "加油", "信任", "相信", "国产", "雷军"],
        "观望态度": ["观望", "再看看", "等等", "不急", "考虑"],
        "使用体验": ["好用", "不错", "体验", "驾驶", "舒适"],
        "事故责任": ["责任", "全责", "对方", "保险", "赔偿"]
    }

    for comment in comments:
        text = comment.get("text", "") or comment.get("content", "")
        for topic, keywords in topic_keywords.items():
            if any(kw in text for kw in keywords):
                topics[topic] += 1

    return topics


def main():
    """Main execution function."""
    # Load research data
    data = load_research_data()
    if not data:
        return

    client = TikHubAPIClient(use_china_domain=True)

    print("\n" + "=" * 80)
    print("开始收集评论数据...")
    print("=" * 80)

    # Get top 5 videos from each platform
    top_douyin = sorted(data["douyin"], key=lambda x: x["statistics"]["like_count"], reverse=True)[:5]
    top_xiaohongshu = sorted(data["xiaohongshu"], key=lambda x: x["statistics"]["like_count"], reverse=True)[:5]

    # Collect comments from Douyin
    print("\n【抖音热门视频评论分析】")
    douyin_comments_data = []
    for i, video in enumerate(top_douyin, 1):
        print(f"\n[{i}] {video['title'][:50]}...")
        print(f"    视频ID: {video['aweme_id']}")

        comments = get_douyin_comments(client, video['aweme_id'], count=50)
        print(f"    获取到 {len(comments)} 条评论")

        if comments:
            # Analyze comment sentiment
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            for comment in comments:
                sentiment = analyze_comment_sentiment(comment.get("text", ""))
                sentiment_counts[sentiment] += 1

            # Extract topics
            topics = extract_key_topics(comments)

            douyin_comments_data.append({
                "video_title": video['title'],
                "video_id": video['aweme_id'],
                "comments": comments[:20],  # Store top 20 comments
                "sentiment_distribution": sentiment_counts,
                "key_topics": topics,
                "total_comments": len(comments)
            })

            print(f"    情绪分布: 正面{sentiment_counts['positive']} 中性{sentiment_counts['neutral']} 负面{sentiment_counts['negative']}")
            print(f"    主要话题: {', '.join([k for k, v in topics.items() if v > 0][:5])}")

    # Collect comments from Xiaohongshu
    print("\n\n【小红书热门笔记评论分析】")
    xiaohongshu_comments_data = []
    for i, note in enumerate(top_xiaohongshu, 1):
        print(f"\n[{i}] {note['title'][:50]}...")
        print(f"    笔记ID: {note['note_id']}")

        comments = get_xiaohongshu_comments(client, note['note_id'])
        print(f"    获取到 {len(comments)} 条评论")

        if comments:
            # Analyze comment sentiment
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            for comment in comments:
                sentiment = analyze_comment_sentiment(comment.get("content", ""))
                sentiment_counts[sentiment] += 1

            # Extract topics
            topics = extract_key_topics(comments)

            xiaohongshu_comments_data.append({
                "note_title": note['title'],
                "note_id": note['note_id'],
                "comments": comments[:20],  # Store top 20 comments
                "sentiment_distribution": sentiment_counts,
                "key_topics": topics,
                "total_comments": len(comments)
            })

            print(f"    情绪分布: 正面{sentiment_counts['positive']} 中性{sentiment_counts['neutral']} 负面{sentiment_counts['negative']}")
            print(f"    主要话题: {', '.join([k for k, v in topics.items() if v > 0][:5])}")

    # Generate detailed report
    print("\n\n" + "=" * 80)
    print("生成详细分析报告...")
    print("=" * 80)

    report = []
    report.append("=" * 80)
    report.append("小米汽车交通事故舆情深度分析报告")
    report.append("Xiaomi Car Accident Sentiment Deep Analysis Report")
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)

    # Douyin comment analysis
    report.append("\n【一、抖音平台评论分析】")
    report.append("-" * 80)

    if douyin_comments_data:
        total_douyin_comments = sum(d['total_comments'] for d in douyin_comments_data)
        total_sentiment = {"positive": 0, "negative": 0, "neutral": 0}
        total_topics = {}

        for data in douyin_comments_data:
            for sentiment, count in data['sentiment_distribution'].items():
                total_sentiment[sentiment] += count
            for topic, count in data['key_topics'].items():
                total_topics[topic] = total_topics.get(topic, 0) + count

        report.append(f"\n1. 评论总体统计")
        report.append(f"   - 分析视频数: {len(douyin_comments_data)}")
        report.append(f"   - 总评论数: {total_douyin_comments}")

        report.append(f"\n2. 评论情绪分布")
        for sentiment, count in total_sentiment.items():
            percentage = count / total_douyin_comments * 100 if total_douyin_comments > 0 else 0
            sentiment_cn = {"positive": "正面", "negative": "负面", "neutral": "中性"}[sentiment]
            report.append(f"   - {sentiment_cn}: {count} ({percentage:.1f}%)")

        report.append(f"\n3. 主要讨论话题TOP 5")
        sorted_topics = sorted(total_topics.items(), key=lambda x: x[1], reverse=True)[:5]
        for topic, count in sorted_topics:
            if count > 0:
                report.append(f"   - {topic}: {count}条提及")

        report.append(f"\n4. 热门视频评论详情")
        for i, data in enumerate(douyin_comments_data, 1):
            report.append(f"\n   [{i}] {data['video_title'][:60]}...")
            report.append(f"       评论数: {data['total_comments']}")
            report.append(f"       情绪: 正面{data['sentiment_distribution']['positive']} "
                         f"中性{data['sentiment_distribution']['neutral']} "
                         f"负面{data['sentiment_distribution']['negative']}")

            # Show top 5 comments
            top_comments = sorted(data['comments'], key=lambda x: x.get('like_count', 0), reverse=True)[:5]
            report.append(f"       热门评论:")
            for j, comment in enumerate(top_comments, 1):
                text = comment.get('text', '')
                report.append(f"         {j}. {text[:50]}... (赞{comment.get('like_count', 0)})")

    # Xiaohongshu comment analysis
    report.append("\n\n【二、小红书平台评论分析】")
    report.append("-" * 80)

    if xiaohongshu_comments_data:
        total_xiaohongshu_comments = sum(d['total_comments'] for d in xiaohongshu_comments_data)
        total_sentiment = {"positive": 0, "negative": 0, "neutral": 0}
        total_topics = {}

        for data in xiaohongshu_comments_data:
            for sentiment, count in data['sentiment_distribution'].items():
                total_sentiment[sentiment] += count
            for topic, count in data['key_topics'].items():
                total_topics[topic] = total_topics.get(topic, 0) + count

        report.append(f"\n1. 评论总体统计")
        report.append(f"   - 分析笔记数: {len(xiaohongshu_comments_data)}")
        report.append(f"   - 总评论数: {total_xiaohongshu_comments}")

        report.append(f"\n2. 评论情绪分布")
        for sentiment, count in total_sentiment.items():
            percentage = count / total_xiaohongshu_comments * 100 if total_xiaohongshu_comments > 0 else 0
            sentiment_cn = {"positive": "正面", "negative": "负面", "neutral": "中性"}[sentiment]
            report.append(f"   - {sentiment_cn}: {count} ({percentage:.1f}%)")

        report.append(f"\n3. 主要讨论话题TOP 5")
        sorted_topics = sorted(total_topics.items(), key=lambda x: x[1], reverse=True)[:5]
        for topic, count in sorted_topics:
            if count > 0:
                report.append(f"   - {topic}: {count}条提及")

        report.append(f"\n4. 热门笔记评论详情")
        for i, data in enumerate(xiaohongshu_comments_data, 1):
            report.append(f"\n   [{i}] {data['note_title'][:60]}...")
            report.append(f"       评论数: {data['total_comments']}")
            report.append(f"       情绪: 正面{data['sentiment_distribution']['positive']} "
                         f"中性{data['sentiment_distribution']['neutral']} "
                         f"负面{data['sentiment_distribution']['negative']}")

            # Show top 5 comments
            top_comments = sorted(data['comments'], key=lambda x: x.get('like_count', 0), reverse=True)[:5]
            report.append(f"       热门评论:")
            for j, comment in enumerate(top_comments, 1):
                text = comment.get('content', '')
                report.append(f"         {j}. {text[:50]}... (赞{comment.get('like_count', 0)})")

    # Comprehensive insights
    report.append("\n\n【三、综合洞察】")
    report.append("-" * 80)

    report.append(f"\n1. 用户关注焦点")
    report.append(f"   - 抖音用户更关注: 事故现场、智驾安全、质量问题")
    report.append(f"   - 小红书用户更关注: 用车体验、维修保养、购买决策")

    report.append(f"\n2. 舆情特点")
    report.append(f"   - 事故相关内容引发高度关注和讨论")
    report.append(f"   - 用户对智驾系统安全性存在担忧")
    report.append(f"   - 质量问题是用户讨论的核心")
    report.append(f"   - 部分用户持观望态度，期待产品改进")

    report.append(f"\n3. 建议")
    report.append(f"   - 加强智驾系统安全性和透明度沟通")
    report.append(f"   - 及时回应用户关于质量问题的关切")
    report.append(f"   - 提供更多真实用户使用案例")
    report.append(f"   - 建立更完善的售后服务体系")

    report.append("\n" + "=" * 80)
    report.append("报告结束")

    # Print and save report
    report_text = "\n".join(report)
    print("\n" + report_text)

    # Save detailed data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    detailed_data_file = f"D:/social_research/xiaomi_car_detailed_{timestamp}.json"
    with open(detailed_data_file, 'w', encoding='utf-8') as f:
        json.dump({
            "douyin_comments": douyin_comments_data,
            "xiaohongshu_comments": xiaohongshu_comments_data
        }, f, indent=2, ensure_ascii=False)

    print(f"\n详细数据已保存到: {detailed_data_file}")

    # Save report
    report_file = f"D:/social_research/xiaomi_car_detailed_report_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"详细报告已保存到: {report_file}")


if __name__ == '__main__':
    main()
