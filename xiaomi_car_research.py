#!/usr/bin/env python3
"""
小米汽车交通事故舆情研究脚本
Xiaomi Car Accident Sentiment Research Script

Collects data from Douyin and Xiaohongshu about Xiaomi car accidents.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Import TikHub API client
sys.path.insert(0, str(Path(__file__).parent / '.claude' / 'skills' / 'tikhub-api-helper'))
from api_client import TikHubAPIClient


class XiaomiCarResearcher:
    """Researcher for Xiaomi car accident sentiment on social media."""

    def __init__(self):
        """Initialize the researcher with API client."""
        self.client = TikHubAPIClient(use_china_domain=True)
        self.results = {
            "douyin": [],
            "xiaohongshu": [],
            "summary": {}
        }

    def search_douyin(self, keyword: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        Search Douyin for videos about Xiaomi car accidents.

        Args:
            keyword: Search keyword
            count: Number of results to fetch

        Returns:
            List of video data
        """
        print(f"\n=== 抖音搜索: {keyword} ===")

        # Use Douyin Search API V2 (general search which includes videos)
        result = self.client.post(
            "/api/v1/douyin/search/fetch_general_search_v2",
            body={
                "keyword": keyword,
                "count": count,
                "sort_type": "0",  # 0: 综合排序
                "publish_time": "0",  # 0: 全部时间
                "filter_duration": "0",  # 0: 全部时长
                "content_type": "0"  # 0: 全部内容
            }
        )

        if "error" in result or result.get("code") != 200:
            error_msg = result.get("error") or result.get("message", "Unknown error")
            print(f"Error searching Douyin: {error_msg}")
            return []

        videos = []
        data = result.get("data", {})

        # Extract video data from response structure
        business_data = data.get("business_data", [])
        for item in business_data:
            if item.get("type") == 1:  # Type 1 is video
                video_data = item.get("data", {})
                video_info = self._parse_douyin_video(video_data)
                if video_info:
                    videos.append(video_info)

        print(f"Found {len(videos)} videos")
        return videos

    def search_xiaohongshu(self, keyword: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        Search Xiaohongshu for notes about Xiaomi car accidents.

        Args:
            keyword: Search keyword
            count: Number of results to fetch

        Returns:
            List of note data
        """
        print(f"\n=== 小红书搜索: {keyword} ===")

        # Use Xiaohongshu Web API v3
        result = self.client.get(
            "/api/v1/xiaohongshu/web/search_notes_v3",
            params={
                "keyword": keyword,
                "page": "1"
            }
        )

        if "error" in result or result.get("code") != 200:
            error_msg = result.get("error") or result.get("message", "Unknown error")
            print(f"Error searching Xiaohongshu: {error_msg}")
            return []

        notes = []
        data = result.get("data", {})
        items_data = data.get("data", {})
        items = items_data.get("items", [])

        # Extract note data from response
        for item in items:
            if item.get("model_type") == "note":
                note_data = item.get("note", {})
                note_info = self._parse_xiaohongshu_note(note_data)
                if note_info:
                    notes.append(note_info)
                    if len(notes) >= count:
                        break

        print(f"Found {len(notes)} notes")
        return notes

    def _parse_douyin_video(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Douyin video data from API response."""
        try:
            # Handle different response structures
            aweme_info = item.get("aweme_info", {})

            return {
                "aweme_id": aweme_info.get("aweme_id", ""),
                "title": aweme_info.get("desc", ""),
                "author": {
                    "uid": aweme_info.get("author", {}).get("uid", ""),
                    "nickname": aweme_info.get("author", {}).get("nickname", ""),
                    "follower_count": aweme_info.get("author", {}).get("follower_count", 0)
                },
                "statistics": {
                    "play_count": aweme_info.get("statistics", {}).get("play_count", 0),
                    "like_count": aweme_info.get("statistics", {}).get("digg_count", 0),
                    "comment_count": aweme_info.get("statistics", {}).get("comment_count", 0),
                    "share_count": aweme_info.get("statistics", {}).get("share_count", 0)
                },
                "create_time": aweme_info.get("create_time", 0),
                "video_url": aweme_info.get("video", {}).get("play_addr", {}).get("url_list", [""])[0] if aweme_info.get("video", {}).get("play_addr", {}).get("url_list") else ""
            }
        except Exception as e:
            print(f"Error parsing video: {e}")
            return None

    def _parse_xiaohongshu_note(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Xiaohongshu note data from API response."""
        try:
            return {
                "note_id": item.get("id", ""),
                "title": item.get("title", ""),
                "desc": item.get("desc", ""),
                "type": item.get("type", ""),
                "author": {
                    "user_id": item.get("user", {}).get("userid", ""),
                    "nickname": item.get("user", {}).get("nickname", ""),
                    "follower_count": 0  # Not available in search response
                },
                "statistics": {
                    "like_count": item.get("liked_count", 0),
                    "collect_count": item.get("collected_count", 0),
                    "comment_count": item.get("comments_count", 0),
                    "share_count": item.get("shared_count", 0)
                },
                "cover_url": item.get("images_list", [{}])[0].get("url", "") if item.get("images_list") else "",
                "time": item.get("last_update_time", 0)
            }
        except Exception as e:
            print(f"Error parsing note: {e}")
            return None

    def get_douyin_comments(self, aweme_id: str, count: int = 20) -> List[Dict[str, Any]]:
        """Get comments for a Douyin video."""
        result = self.client.get(
            "/api/v1/douyin/web/fetch_video_comments",
            params={
                "aweme_id": aweme_id,
                "count": count
            }
        )

        if "error" in result:
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

    def get_xiaohongshu_comments(self, note_id: str, count: int = 20) -> List[Dict[str, Any]]:
        """Get comments for a Xiaohongshu note."""
        result = self.client.get(
            "/api/v1/xiaohongshu/web_v2/fetch_note_comments",
            params={
                "note_id": note_id,
                "cursor": "0",
                "top_comment_id": ""
            }
        )

        if "error" in result:
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

    def analyze_sentiment(self, text: str) -> str:
        """
        Simple sentiment analysis based on keywords.
        Returns: 'positive', 'neutral', 'negative'
        """
        negative_keywords = [
            "事故", "车祸", "伤亡", "死", "伤", "危险", "问题", "缺陷",
            "失控", "碰撞", "追尾", "起火", "刹车", "失灵", "安全隐患"
        ]

        positive_keywords = [
            "安全", "好", "优秀", "可靠", "信任", "喜欢", "推荐", "不错",
            "稳定", "放心", "体验好", "质量好"
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

    def collect_data(self):
        """Collect data from both platforms."""
        # Search keywords
        keywords = [
            "小米汽车事故",
            "小米SU7事故",
            "小米汽车车祸",
            "小米SU7"
        ]

        print("=" * 60)
        print("开始收集数据...")
        print("=" * 60)

        # Collect Douyin data
        print("\n【抖音平台数据收集】")
        for keyword in keywords:
            videos = self.search_douyin(keyword, count=20)
            for video in videos:
                # Add search keyword
                video["search_keyword"] = keyword

                # Analyze sentiment
                title = video.get("title", "")
                video["sentiment"] = self.analyze_sentiment(title)

                self.results["douyin"].append(video)

        # Collect Xiaohongshu data
        print("\n【小红书平台数据收集】")
        for keyword in keywords:
            notes = self.search_xiaohongshu(keyword, count=20)
            for note in notes:
                # Add search keyword
                note["search_keyword"] = keyword

                # Analyze sentiment
                title = note.get("title", "") + " " + note.get("desc", "")
                note["sentiment"] = self.analyze_sentiment(title)

                self.results["xiaohongshu"].append(note)

        # Generate summary
        self._generate_summary()

    def _generate_summary(self):
        """Generate summary statistics."""
        print("\n【生成统计摘要】")

        # Douyin summary
        douyin_total = len(self.results["douyin"])
        douyin_sentiment = {}
        douyin_total_plays = 0
        douyin_total_likes = 0
        douyin_total_comments = 0

        for video in self.results["douyin"]:
            sentiment = video.get("sentiment", "neutral")
            douyin_sentiment[sentiment] = douyin_sentiment.get(sentiment, 0) + 1
            douyin_total_plays += video["statistics"]["play_count"]
            douyin_total_likes += video["statistics"]["like_count"]
            douyin_total_comments += video["statistics"]["comment_count"]

        # Xiaohongshu summary
        xiaohongshu_total = len(self.results["xiaohongshu"])
        xiaohongshu_sentiment = {}
        xiaohongshu_total_likes = 0
        xiaohongshu_total_collects = 0
        xiaohongshu_total_comments = 0

        for note in self.results["xiaohongshu"]:
            sentiment = note.get("sentiment", "neutral")
            xiaohongshu_sentiment[sentiment] = xiaohongshu_sentiment.get(sentiment, 0) + 1
            xiaohongshu_total_likes += note["statistics"]["like_count"]
            xiaohongshu_total_collects += note["statistics"]["collect_count"]
            xiaohongshu_total_comments += note["statistics"]["comment_count"]

        self.results["summary"] = {
            "douyin": {
                "total_videos": douyin_total,
                "sentiment_distribution": douyin_sentiment,
                "total_plays": douyin_total_plays,
                "total_likes": douyin_total_likes,
                "total_comments": douyin_total_comments,
                "avg_likes": douyin_total_likes / douyin_total if douyin_total > 0 else 0
            },
            "xiaohongshu": {
                "total_notes": xiaohongshu_total,
                "sentiment_distribution": xiaohongshu_sentiment,
                "total_likes": xiaohongshu_total_likes,
                "total_collects": xiaohongshu_total_collects,
                "total_comments": xiaohongshu_total_comments,
                "avg_likes": xiaohongshu_total_likes / xiaohongshu_total if xiaohongshu_total > 0 else 0
            }
        }

    def generate_report(self) -> str:
        """Generate a comprehensive report."""
        report = []
        report.append("=" * 80)
        report.append("小米汽车交通事故舆情分析报告")
        report.append("Xiaomi Car Accident Sentiment Analysis Report")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)

        # Douyin section
        report.append("\n【一、抖音平台分析】")
        report.append("-" * 80)

        douyin_summary = self.results["summary"]["douyin"]
        report.append(f"\n1. 数据概况")
        report.append(f"   - 视频总数: {douyin_summary['total_videos']}")
        report.append(f"   - 总播放量: {douyin_summary['total_plays']:,}")
        report.append(f"   - 总点赞数: {douyin_summary['total_likes']:,}")
        report.append(f"   - 总评论数: {douyin_summary['total_comments']:,}")
        report.append(f"   - 平均点赞: {douyin_summary['avg_likes']:.1f}")

        report.append(f"\n2. 情绪分布")
        for sentiment, count in douyin_summary['sentiment_distribution'].items():
            percentage = count / douyin_summary['total_videos'] * 100
            sentiment_cn = {"positive": "正面", "negative": "负面", "neutral": "中性"}[sentiment]
            report.append(f"   - {sentiment_cn}: {count} ({percentage:.1f}%)")

        report.append(f"\n3. 热门视频TOP 10")
        # Sort by play count
        top_videos = sorted(
            self.results["douyin"],
            key=lambda x: x["statistics"]["play_count"],
            reverse=True
        )[:10]

        for i, video in enumerate(top_videos, 1):
            sentiment_cn = {"positive": "正面", "negative": "负面", "neutral": "中性"}[video.get("sentiment", "neutral")]
            report.append(f"\n   [{i}] {video['title'][:50]}...")
            report.append(f"       作者: {video['author']['nickname']}")
            report.append(f"       播放: {video['statistics']['play_count']:,} | "
                         f"点赞: {video['statistics']['like_count']:,} | "
                         f"评论: {video['statistics']['comment_count']:,}")
            report.append(f"       情绪: {sentiment_cn}")

        # Xiaohongshu section
        report.append("\n\n【二、小红书平台分析】")
        report.append("-" * 80)

        xiaohongshu_summary = self.results["summary"]["xiaohongshu"]
        report.append(f"\n1. 数据概况")
        report.append(f"   - 笔记总数: {xiaohongshu_summary['total_notes']}")
        report.append(f"   - 总点赞数: {xiaohongshu_summary['total_likes']:,}")
        report.append(f"   - 总收藏数: {xiaohongshu_summary['total_collects']:,}")
        report.append(f"   - 总评论数: {xiaohongshu_summary['total_comments']:,}")
        report.append(f"   - 平均点赞: {xiaohongshu_summary['avg_likes']:.1f}")

        report.append(f"\n2. 情绪分布")
        for sentiment, count in xiaohongshu_summary['sentiment_distribution'].items():
            percentage = count / xiaohongshu_summary['total_notes'] * 100
            sentiment_cn = {"positive": "正面", "negative": "负面", "neutral": "中性"}[sentiment]
            report.append(f"   - {sentiment_cn}: {count} ({percentage:.1f}%)")

        report.append(f"\n3. 热门笔记TOP 10")
        # Sort by like count
        top_notes = sorted(
            self.results["xiaohongshu"],
            key=lambda x: x["statistics"]["like_count"],
            reverse=True
        )[:10]

        for i, note in enumerate(top_notes, 1):
            sentiment_cn = {"positive": "正面", "negative": "负面", "neutral": "中性"}[note.get("sentiment", "neutral")]
            report.append(f"\n   [{i}] {note['title'][:50]}...")
            report.append(f"       作者: {note['author']['nickname']}")
            report.append(f"       点赞: {note['statistics']['like_count']:,} | "
                         f"收藏: {note['statistics']['collect_count']:,} | "
                         f"评论: {note['statistics']['comment_count']:,}")
            report.append(f"       情绪: {sentiment_cn}")

        # Overall analysis
        report.append("\n\n【三、综合分析】")
        report.append("-" * 80)

        total_negative_douyin = douyin_summary['sentiment_distribution'].get('negative', 0)
        total_negative_xiaohongshu = xiaohongshu_summary['sentiment_distribution'].get('negative', 0)

        report.append(f"\n1. 舆情总体特征")
        if douyin_summary['total_videos'] > 0:
            negative_ratio_douyin = total_negative_douyin / douyin_summary['total_videos']
            if negative_ratio_douyin > 0.5:
                report.append(f"   - 抖音平台: 负面情绪占主导 ({negative_ratio_douyin*100:.1f}%)")
            else:
                report.append(f"   - 抖音平台: 情绪相对平衡")
        else:
            report.append(f"   - 抖音平台: 无数据")

        if xiaohongshu_summary['total_notes'] > 0:
            negative_ratio_xiaohongshu = total_negative_xiaohongshu / xiaohongshu_summary['total_notes']
            if negative_ratio_xiaohongshu > 0.5:
                report.append(f"   - 小红书平台: 负面情绪占主导 ({negative_ratio_xiaohongshu*100:.1f}%)")
            else:
                report.append(f"   - 小红书平台: 情绪相对平衡")
        else:
            report.append(f"   - 小红书平台: 无数据")

        report.append(f"\n2. 讨论热度对比")
        if douyin_summary['total_plays'] > xiaohongshu_summary['total_likes'] * 10:
            report.append(f"   - 抖音讨论热度显著更高 (视频属性)")
        else:
            report.append(f"   - 两个平台讨论热度相当")

        report.append(f"\n3. 内容类型分析")
        accident_keywords = ["事故", "车祸", "碰撞"]
        douyin_accident_count = sum(1 for v in self.results["douyin"]
                                   if any(kw in v['title'] for kw in accident_keywords))
        xiaohongshu_accident_count = sum(1 for n in self.results["xiaohongshu"]
                                        if any(kw in n['title'] or kw in n.get('desc', '') for kw in accident_keywords))

        if douyin_summary['total_videos'] > 0:
            report.append(f"   - 抖音事故相关内容: {douyin_accident_count}/{douyin_summary['total_videos']} "
                         f"({douyin_accident_count/douyin_summary['total_videos']*100:.1f}%)")
        else:
            report.append(f"   - 抖音事故相关内容: 无数据")

        if xiaohongshu_summary['total_notes'] > 0:
            report.append(f"   - 小红书事故相关内容: {xiaohongshu_accident_count}/{xiaohongshu_summary['total_notes']} "
                         f"({xiaohongshu_accident_count/xiaohongshu_summary['total_notes']*100:.1f}%)")
        else:
            report.append(f"   - 小红书事故相关内容: 无数据")

        report.append("\n" + "=" * 80)
        report.append("报告结束")

        return "\n".join(report)

    def save_results(self, filename: str = None):
        """Save results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"D:/social_research/xiaomi_car_research_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n数据已保存到: {filename}")

    def save_report(self, filename: str = None):
        """Save report to text file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"D:/social_research/xiaomi_car_report_{timestamp}.txt"

        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"报告已保存到: {filename}")


def main():
    """Main execution function."""
    researcher = XiaomiCarResearcher()

    # Collect data
    researcher.collect_data()

    # Generate and display report
    report = researcher.generate_report()
    print("\n" + report)

    # Save results
    researcher.save_results()
    researcher.save_report()


if __name__ == '__main__':
    main()
