with source as (

    select distinct * from {{ source('raw', 'subscriptions') }}

),

cleaned as (

    select
        subscription_id,
        account_id,
        plan,
        mrr,
        cast(start_date as date) as start_date,
        cast(end_date as date) as end_date,
        case
            when lower(trim(status)) in ('active', 'live') then 'active'
            when lower(trim(status)) in ('ended', 'cancelled') then 'ended'
            else 'unknown'
        end as status
    from source

),

flagged as (

    select
        *,
        status = 'ended' and end_date is null as end_date_missing,
        status = 'active' and end_date < date '2025-12-01' as active_but_ended_earlier
    from cleaned

)

select * from flagged