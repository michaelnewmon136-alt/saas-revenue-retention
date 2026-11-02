with source as (

    select distinct * from {{ source('raw', 'subscription_events') }}

),

cleaned as (

    select
        event_id,
        account_id,
        cast(event_date as date) as event_date,
        case
            when lower(trim(event_type)) = 'new' then 'new'
            when lower(trim(event_type)) = 'upgrade' then 'upgrade'
            when lower(trim(event_type)) = 'downgrade' then 'downgrade'
            when lower(trim(event_type)) in ('cancel', 'cancelled', 'canceled', 'churned') then 'cancel'
            when lower(trim(event_type)) in ('reactivate', 'reactivated', 'reactivation') then 'reactivate'
            else 'unknown'
        end as event_type,
        old_mrr,
        new_mrr,
        new_mrr is null as new_mrr_missing
    from source

)

select * from cleaned