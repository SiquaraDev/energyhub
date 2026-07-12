## 1. Auth Domain Entities

- [x] 1.1 Create User entity in auth/domain/entity/user.py extending BaseEntity
- [x] 1.2 Add username field to User entity
- [x] 1.3 Add password field to User entity
- [x] 1.4 Add email field to User entity
- [x] 1.5 Add full_name optional field to User entity
- [x] 1.6 Add active field defaulting to True to User entity
- [x] 1.7 Add roles list with default factory to User entity
- [x] 1.8 Create Role entity in auth/domain/entity/role.py extending BaseEntity
- [x] 1.9 Add name field to Role entity
- [x] 1.10 Add description optional field to Role entity
- [x] 1.11 Add permissions list with default factory to Role entity
- [x] 1.12 Create Permission entity in auth/domain/entity/permission.py extending BaseEntity
- [x] 1.13 Add name field to Permission entity
- [x] 1.14 Add description optional field to Permission entity
- [x] 1.15 Model relationships between User, Role, and Permission as plain Python references (lists) — ORM mapping deferred to Fase 5

## 2. Clients Domain Entities

- [x] 2.1 Create Client entity in clients/domain/entity/client.py extending BaseEntity
- [x] 2.2 Add cnpj field to Client entity
- [x] 2.3 Add corporate_name field to Client entity
- [x] 2.4 Add trade_name optional field to Client entity
- [x] 2.5 Add email optional field to Client entity
- [x] 2.6 Add phone optional field to Client entity
- [x] 2.7 Add address optional field to Client entity
- [x] 2.8 Add city optional field to Client entity
- [x] 2.9 Add state optional field to Client entity
- [x] 2.10 Add zip_code optional field to Client entity
- [x] 2.11 Add active field defaulting to True to Client entity
- [x] 2.12 Add contacts list with default factory to Client entity
- [x] 2.13 Create Contact entity in clients/domain/entity/contact.py extending BaseEntity
- [x] 2.14 Add client_id field to Contact entity
- [x] 2.15 Add name field to Contact entity
- [x] 2.16 Add email optional field to Contact entity
- [x] 2.17 Add phone optional field to Contact entity
- [x] 2.18 Add position optional field to Contact entity
- [x] 2.19 Add type field using ContactType enum to Contact entity
- [x] 2.20 Add optional client reference to Contact entity
- [x] 2.21 Model relationships between Client and Contact as plain Python references — ORM mapping deferred to Fase 5

## 3. Contracts Domain Entities

- [x] 3.1 Create Contract entity in contracts/domain/entity/contract.py extending BaseEntity
- [x] 3.2 Add contract_number field to Contract entity
- [x] 3.3 Add client_id field to Contract entity
- [x] 3.4 Add start_date field to Contract entity
- [x] 3.5 Add end_date field to Contract entity
- [x] 3.6 Add energy_amount field using Decimal to Contract entity
- [x] 3.7 Add unit_price field using Decimal to Contract entity
- [x] 3.8 Add total_value field using Decimal to Contract entity
- [x] 3.9 Add status field using ContractStatus enum to Contract entity
- [x] 3.10 Add type field using ContractType enum to Contract entity
- [x] 3.11 Add optional client reference to Contract entity
- [x] 3.12 Implement approve method in Contract entity with validation
- [x] 3.13 Implement activate method in Contract entity with validation
- [x] 3.14 Create InvalidContractStatusException in contracts/domain/exception/

## 4. Negotiations Domain Entities

- [x] 4.1 Create Negotiation entity in negotiations/domain/entity/negotiation.py extending BaseEntity
- [x] 4.2 Add contract_id field to Negotiation entity
- [x] 4.3 Add status field using NegotiationStatus enum to Negotiation entity
- [x] 4.4 Add optional contract reference to Negotiation entity
- [x] 4.5 Create EnergyTransaction entity in negotiations/domain/entity/energy_transaction.py extending BaseEntity
- [x] 4.6 Add negotiation_id field to EnergyTransaction entity
- [x] 4.7 Add amount field using Decimal to EnergyTransaction entity
- [x] 4.8 Add price field using Decimal to EnergyTransaction entity
- [x] 4.9 Add type field using TransactionType enum to EnergyTransaction entity
- [x] 4.10 Add transaction_date field to EnergyTransaction entity
- [x] 4.11 Add optional negotiation reference to EnergyTransaction entity
- [x] 4.12 Model relationships between Negotiation and EnergyTransaction as plain Python references (aggregate-managed) — ORM mapping deferred to Fase 5
- [x] 4.13 Create InvalidNegotiationException in negotiations/domain/exception/

## 5. Financial Domain Entities

- [x] 5.1 Create Invoice entity in financial/domain/entity/invoice.py extending BaseEntity
- [x] 5.2 Add invoice_number field to Invoice entity
- [x] 5.3 Add client_id field to Invoice entity
- [x] 5.4 Add amount field using Decimal to Invoice entity
- [x] 5.5 Add due_date field to Invoice entity
- [x] 5.6 Add status field using InvoiceStatus enum to Invoice entity
- [x] 5.7 Add optional client reference to Invoice entity
- [x] 5.8 Create Payment entity in financial/domain/entity/payment.py extending BaseEntity
- [x] 5.9 Add invoice_id field to Payment entity
- [x] 5.10 Add amount field using Decimal to Payment entity
- [x] 5.11 Add payment_date field to Payment entity
- [x] 5.12 Add optional invoice reference to Payment entity
- [x] 5.13 Model relationships between Invoice and Payment as plain Python references (aggregate-managed) — ORM mapping deferred to Fase 5

## 6. Audit Domain Entities

- [x] 6.1 Create AuditLog entity in audit/domain/entity/audit_log.py extending BaseEntity
- [x] 6.2 Add user_id field to AuditLog entity
- [x] 6.3 Add action field using AuditAction enum to AuditLog entity
- [x] 6.4 Add entity_type field to AuditLog entity
- [x] 6.5 Add entity_id field to AuditLog entity
- [x] 6.6 Add details field to AuditLog entity
- [x] 6.7 Add timestamp field to AuditLog entity
- [x] 6.8 Add optional user reference to AuditLog entity

## 7. Notifications Domain Entities

- [x] 7.1 Create Notification entity in notifications/domain/entity/notification.py extending BaseEntity
- [x] 7.2 Add user_id field to Notification entity
- [x] 7.3 Add title field to Notification entity
- [x] 7.4 Add message field to Notification entity
- [x] 7.5 Add status field using NotificationStatus enum to Notification entity
- [x] 7.6 Add optional user reference to Notification entity

## 8. Reports Domain Entities

- [x] 8.1 Create Report entity in reports/domain/entity/report.py extending BaseEntity
- [x] 8.2 Add report_type field to Report entity
- [x] 8.3 Add generated_by field to Report entity
- [x] 8.4 Add parameters field to Report entity
- [x] 8.5 Add file_path field to Report entity
- [x] 8.6 Add status field to Report entity

## 9. Domain Enums

- [x] 9.1 Create ContactType enum in clients/domain/entity/contact_type.py
- [x] 9.2 Add PRIMARY value to ContactType enum
- [x] 9.3 Add BILLING value to ContactType enum
- [x] 9.4 Add TECHNICAL value to ContactType enum
- [x] 9.5 Add COMMERCIAL value to ContactType enum
- [x] 9.6 Create ContractStatus enum in contracts/domain/entity/contract_status.py
- [x] 9.7 Add DRAFT value to ContractStatus enum
- [x] 9.8 Add PENDING_APPROVAL value to ContractStatus enum
- [x] 9.9 Add APPROVED value to ContractStatus enum
- [x] 9.10 Add ACTIVE value to ContractStatus enum
- [x] 9.11 Add SUSPENDED value to ContractStatus enum
- [x] 9.12 Add TERMINATED value to ContractStatus enum
- [x] 9.13 Add EXPIRED value to ContractStatus enum
- [x] 9.14 Create ContractType enum in contracts/domain/entity/contract_type.py
- [x] 9.15 Add PURCHASE value to ContractType enum
- [x] 9.16 Add SALE value to ContractType enum
- [x] 9.17 Add BIDIRECTIONAL value to ContractType enum
- [x] 9.18 Create NegotiationStatus enum in negotiations/domain/entity/negotiation_status.py
- [x] 9.19 Add DRAFT value to NegotiationStatus enum
- [x] 9.20 Add IN_PROGRESS value to NegotiationStatus enum
- [x] 9.21 Add COMPLETED value to NegotiationStatus enum
- [x] 9.22 Add CANCELLED value to NegotiationStatus enum
- [x] 9.23 Create TransactionType enum in negotiations/domain/entity/transaction_type.py
- [x] 9.24 Add BUY value to TransactionType enum
- [x] 9.25 Add SELL value to TransactionType enum
- [x] 9.26 Create InvoiceStatus enum in financial/domain/entity/invoice_status.py
- [x] 9.27 Add DRAFT value to InvoiceStatus enum
- [x] 9.28 Add ISSUED value to InvoiceStatus enum
- [x] 9.29 Add PAID value to InvoiceStatus enum
- [x] 9.30 Add OVERDUE value to InvoiceStatus enum
- [x] 9.31 Add CANCELLED value to InvoiceStatus enum
- [x] 9.32 Create NotificationStatus enum in notifications/domain/entity/notification_status.py
- [x] 9.33 Add PENDING value to NotificationStatus enum
- [x] 9.34 Add SENT value to NotificationStatus enum
- [x] 9.35 Add READ value to NotificationStatus enum
- [x] 9.36 Add FAILED value to NotificationStatus enum
- [x] 9.37 Create AuditAction enum in audit/domain/entity/audit_action.py
- [x] 9.38 Add CREATE value to AuditAction enum
- [x] 9.39 Add UPDATE value to AuditAction enum
- [x] 9.40 Add DELETE value to AuditAction enum
- [x] 9.41 Add LOGIN value to AuditAction enum
- [x] 9.42 Add LOGOUT value to AuditAction enum

## 10. Domain Value Objects

- [x] 10.1 Create CNPJ Value Object in shared/domain/valueobject/cnpj.py
- [x] 10.2 Implement CNPJ validation in __post_init__
- [x] 10.3 Implement CNPJ formatting method
- [x] 10.4 Create Email Value Object in shared/domain/valueobject/email.py
- [x] 10.5 Implement email validation in __post_init__
- [x] 10.6 Implement email lowercase conversion
- [x] 10.7 Create Money Value Object in shared/domain/valueobject/money.py
- [x] 10.8 Add amount field using Decimal to Money
- [x] 10.9 Add currency field to Money
- [x] 10.10 Create PhoneNumber Value Object in shared/domain/valueobject/phone_number.py
- [x] 10.11 Implement phone validation in __post_init__
- [x] 10.12 Create Address Value Object in shared/domain/valueobject/address.py
- [x] 10.13 Add street field to Address
- [x] 10.14 Add city field to Address
- [x] 10.15 Add state field to Address
- [x] 10.16 Add zip_code field to Address
- [x] 10.17 Add country field to Address
- [x] 10.18 Create Percentage Value Object in shared/domain/valueobject/percentage.py
- [x] 10.19 Add value field using Decimal to Percentage
- [x] 10.20 Implement percentage validation (0-100) in __post_init__

## 11. Domain Aggregates

- [x] 11.1 Create AuthAggregate in auth/domain/auth_aggregate.py
- [x] 11.2 Implement User as aggregate root in AuthAggregate
- [x] 11.3 Implement role management methods in AuthAggregate
- [x] 11.4 Create ClientAggregate in clients/domain/client_aggregate.py
- [x] 11.5 Implement Client as aggregate root in ClientAggregate
- [x] 11.6 Implement add_contact method in ClientAggregate
- [x] 11.7 Implement remove_contact method in ClientAggregate
- [x] 11.8 Implement activate method in ClientAggregate
- [x] 11.9 Implement deactivate method in ClientAggregate
- [x] 11.10 Implement get_client method in ClientAggregate
- [x] 11.11 Create ContractAggregate in contracts/domain/contract_aggregate.py
- [x] 11.12 Implement Contract as aggregate root in ContractAggregate
- [x] 11.13 Enforce business rules in ContractAggregate
- [x] 11.14 Create NegotiationAggregate in negotiations/domain/negotiation_aggregate.py
- [x] 11.15 Implement Negotiation as aggregate root in NegotiationAggregate
- [x] 11.16 Manage EnergyTransaction entities in NegotiationAggregate
- [x] 11.17 Create FinancialAggregate in financial/domain/financial_aggregate.py
- [x] 11.18 Implement Invoice as aggregate root in FinancialAggregate
- [x] 11.19 Manage Payment entities in FinancialAggregate
- [x] 11.20 Create InvalidClientStateException in clients/domain/exception/

## 12. Domain Validations

- [x] 12.1 Add __post_init__ validation for username in User entity
- [x] 12.2 Implement username validation (not empty)
- [x] 12.3 Add __post_init__ validation for email in User entity
- [x] 12.4 Implement email validation (contains @)
- [x] 12.5 Implement add_role helper method in User entity
- [x] 12.6 Implement remove_role helper method in User entity
- [x] 12.7 Add relationship helper methods to other entities as needed
- [x] 12.8 Verify all validators are working correctly

## 13. Validation

- [x] 13.1 Verify all domain entities are created
- [x] 13.2 Verify relationships are configured correctly
- [x] 13.3 Verify all enums are created with correct values
- [x] 13.4 Verify all Value Objects are created with validation
- [x] 13.5 Verify all aggregates are defined with aggregate roots
- [x] 13.6 Verify domain rules are implemented in entities
- [x] 13.7 Run application to ensure no import errors
- [x] 13.8 Test that domain model compiles without errors
