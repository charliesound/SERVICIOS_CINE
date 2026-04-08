from typing import Any, Dict, List, Optional

from src.storage.sqlite_sequence_plan_runs_store import SQLiteSequencePlanRunsStore


class SequencePlanRunsRepository:
    def __init__(self, store: SQLiteSequencePlanRunsStore):
        self.store = store

    def create(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.create_run(run_data)

    def get(self, request_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_run(request_id)

    def update(self, request_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.store.update_run(request_id, updates)

    def list_prompt_comparisons(self, request_id: str) -> List[Dict[str, Any]]:
        run = self.store.get_run(request_id)
        if run is None:
            return []
        comparisons = run.get("prompt_comparisons") if isinstance(run.get("prompt_comparisons"), list) else []
        return [item for item in comparisons if isinstance(item, dict)]

    def list_recent(self, limit: Optional[int] = 20) -> List[Dict[str, Any]]:
        return self.store.list_runs(limit)

    def create_review_history_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.create_review_history_entry(entry_data)

    def list_review_history_for_request(self, request_id: str, limit: Optional[int] = 200) -> List[Dict[str, Any]]:
        return self.store.list_review_history_for_request(request_id=request_id, limit=limit)

    def get_review_history_summary(self, request_id: str) -> Dict[str, Any]:
        return self.store.get_review_history_summary(request_id)

    def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.create_notification(notification_data)

    def list_notifications(
        self,
        limit: int = 50,
        collection_id: Optional[str] = None,
        is_read: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        return self.store.list_notifications(limit=limit, collection_id=collection_id, is_read=is_read)

    def get_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_notification(notification_id)

    def update_notification_read(self, notification_id: str, is_read: bool) -> Optional[Dict[str, Any]]:
        return self.store.update_notification_read(notification_id=notification_id, is_read=is_read)

    def get_collection_notification_state(self, collection_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_collection_notification_state(collection_id)

    def upsert_collection_notification_state(self, collection_id: str, state_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.upsert_collection_notification_state(collection_id=collection_id, state_data=state_data)

    def get_notification_preferences(self) -> Dict[str, Any]:
        return self.store.get_notification_preferences()

    def upsert_notification_preferences(self, preferences_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.upsert_notification_preferences(preferences_data)

    def list_webhooks(self, limit: int = 100, include_disabled: bool = True) -> List[Dict[str, Any]]:
        return self.store.list_webhooks(limit=limit, include_disabled=include_disabled)

    def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_webhook(webhook_id)

    def create_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.create_webhook(webhook_data)

    def update_webhook(self, webhook_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.store.update_webhook(webhook_id=webhook_id, updates=updates)

    def create_webhook_delivery(self, delivery_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.create_webhook_delivery(delivery_data)

    def get_webhook_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_webhook_delivery(delivery_id)

    def update_webhook_delivery(self, delivery_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.store.update_webhook_delivery(delivery_id=delivery_id, updates=updates)

    def list_webhook_deliveries(
        self,
        limit: int = 100,
        webhook_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        notification_id: Optional[str] = None,
        is_test: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        return self.store.list_webhook_deliveries(
            limit=limit,
            webhook_id=webhook_id,
            collection_id=collection_id,
            notification_id=notification_id,
            is_test=is_test,
        )

    def list_webhook_deliveries_pending_retry(
        self,
        due_before: str,
        limit: int = 100,
        webhook_id: Optional[str] = None,
        collection_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self.store.list_webhook_deliveries_pending_retry(
            due_before=due_before,
            limit=limit,
            webhook_id=webhook_id,
            collection_id=collection_id,
        )

    def list_webhook_delivery_stats_by_webhook(self) -> List[Dict[str, Any]]:
        return self.store.list_webhook_delivery_stats_by_webhook()

    def list_recent_webhook_delivery_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.store.list_recent_webhook_delivery_errors(limit=limit)

    def list_notification_channels(
        self,
        limit: int = 100,
        include_disabled: bool = True,
        channel_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self.store.list_notification_channels(
            limit=limit,
            include_disabled=include_disabled,
            channel_type=channel_type,
        )

    def get_notification_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_notification_channel(channel_id)

    def create_notification_channel(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.create_notification_channel(channel_data)

    def update_notification_channel(self, channel_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.store.update_notification_channel(channel_id=channel_id, updates=updates)

    def create_notification_channel_delivery(self, delivery_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.create_notification_channel_delivery(delivery_data)

    def get_notification_channel_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_notification_channel_delivery(delivery_id)

    def update_notification_channel_delivery(self, delivery_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.store.update_notification_channel_delivery(delivery_id=delivery_id, updates=updates)

    def list_notification_channel_deliveries(
        self,
        limit: int = 100,
        channel_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        notification_id: Optional[str] = None,
        channel_type: Optional[str] = None,
        is_test: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        return self.store.list_notification_channel_deliveries(
            limit=limit,
            channel_id=channel_id,
            collection_id=collection_id,
            notification_id=notification_id,
            channel_type=channel_type,
            is_test=is_test,
        )

    def list_notification_channel_deliveries_pending_retry(
        self,
        due_before: str,
        limit: int = 100,
        channel_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        channel_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self.store.list_notification_channel_deliveries_pending_retry(
            due_before=due_before,
            limit=limit,
            channel_id=channel_id,
            collection_id=collection_id,
            channel_type=channel_type,
        )

    def list_recent_notification_channel_delivery_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.store.list_recent_notification_channel_delivery_errors(limit=limit)

    def list_alert_routing_rules(
        self,
        limit: int = 100,
        include_disabled: bool = True,
        target_channel_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self.store.list_alert_routing_rules(
            limit=limit,
            include_disabled=include_disabled,
            target_channel_id=target_channel_id,
        )

    def get_alert_routing_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_alert_routing_rule(rule_id)

    def create_alert_routing_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.create_alert_routing_rule(rule_data)

    def update_alert_routing_rule(self, rule_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.store.update_alert_routing_rule(rule_id=rule_id, updates=updates)

    def delete_alert_routing_rule(self, rule_id: str) -> bool:
        return self.store.delete_alert_routing_rule(rule_id)

    def create_collection(self, collection_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.create_collection(collection_data)

    def list_collections(self, limit: int = 100, include_archived: bool = False) -> List[Dict[str, Any]]:
        return self.store.list_collections(limit=limit, include_archived=include_archived)

    def get_collection(self, collection_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_collection(collection_id)

    def update_collection(self, collection_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.store.update_collection(collection_id, updates)

    def delete_collection(self, collection_id: str) -> bool:
        return self.store.delete_collection(collection_id)

    def list_collection_items(self, collection_id: str) -> List[Dict[str, Any]]:
        return self.store.list_collection_items(collection_id)

    def list_collections_for_request(self, request_id: str) -> List[Dict[str, Any]]:
        return self.store.list_collections_for_request(request_id)

    def add_collection_items(
        self,
        collection_id: str,
        request_ids: List[str],
        added_at: str,
        updated_at: str,
    ) -> Dict[str, int]:
        return self.store.add_collection_items(
            collection_id=collection_id,
            request_ids=request_ids,
            added_at=added_at,
            updated_at=updated_at,
        )

    def remove_collection_item(self, collection_id: str, request_id: str, updated_at: str) -> bool:
        return self.store.remove_collection_item(collection_id=collection_id, request_id=request_id, updated_at=updated_at)

    def set_collection_item_highlight(
        self,
        collection_id: str,
        request_id: str,
        is_highlighted: bool,
        updated_at: str,
    ) -> Optional[Dict[str, Any]]:
        return self.store.set_collection_item_highlight(
            collection_id=collection_id,
            request_id=request_id,
            is_highlighted=is_highlighted,
            updated_at=updated_at,
        )
