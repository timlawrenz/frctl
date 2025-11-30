/**
 * Example TypeSpec contract for Order Events
 * 
 * This contract defines the event schema for order-related events
 * that are published to the event bus.
 */

import "@typespec/http";
import "@typespec/rest";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace OrderEvents;

/**
 * Order status enumeration
 */
enum OrderStatus {
  Created: "created",
  Pending: "pending",
  Confirmed: "confirmed",
  Shipped: "shipped",
  Delivered: "delivered",
  Cancelled: "cancelled"
}

/**
 * Base event structure
 */
model BaseEvent {
  /** Unique event identifier */
  eventId: string;
  
  /** Event timestamp (ISO 8601) */
  timestamp: utcDateTime;
  
  /** Event version for schema evolution */
  version: string;
}

/**
 * Order created event
 * 
 * Published when a new order is created in the system.
 */
model OrderCreatedEvent extends BaseEvent {
  /** Order identifier */
  orderId: string;
  
  /** Customer identifier */
  customerId: string;
  
  /** Order items */
  items: OrderItem[];
  
  /** Total amount in cents */
  totalAmount: int32;
  
  /** Currency code (ISO 4217) */
  currency: string;
}

/**
 * Order item details
 */
model OrderItem {
  /** Product SKU */
  sku: string;
  
  /** Quantity */
  quantity: int32;
  
  /** Unit price in cents */
  unitPrice: int32;
}

/**
 * Order status changed event
 * 
 * Published when an order's status changes.
 */
model OrderStatusChangedEvent extends BaseEvent {
  /** Order identifier */
  orderId: string;
  
  /** Previous status */
  oldStatus: OrderStatus;
  
  /** New status */
  newStatus: OrderStatus;
  
  /** Optional reason for status change */
  reason?: string;
}

/**
 * Order cancelled event
 * 
 * Published when an order is cancelled.
 */
model OrderCancelledEvent extends BaseEvent {
  /** Order identifier */
  orderId: string;
  
  /** Cancellation reason */
  reason: string;
  
  /** Refund amount in cents */
  refundAmount: int32;
}

/**
 * Contract validation: These events MUST be published
 * by any service that OWNS the order-events schema.
 */
@doc("Events that order-service MUST publish")
interface OrderEventPublisher {
  /** Publish order created event */
  publishOrderCreated(event: OrderCreatedEvent): void;
  
  /** Publish order status changed event */
  publishOrderStatusChanged(event: OrderStatusChangedEvent): void;
  
  /** Publish order cancelled event */
  publishOrderCancelled(event: OrderCancelledEvent): void;
}

/**
 * Contract validation: These events MAY be consumed
 * by any service that CONSUMES the order-events schema.
 */
@doc("Events that consumers MAY subscribe to")
interface OrderEventConsumer {
  /** Handle order created event */
  onOrderCreated(event: OrderCreatedEvent): void;
  
  /** Handle order status changed event */
  onOrderStatusChanged(event: OrderStatusChangedEvent): void;
  
  /** Handle order cancelled event */
  onOrderCancelled(event: OrderCancelledEvent): void;
}
