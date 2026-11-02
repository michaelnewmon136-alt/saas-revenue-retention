with source as (

    select distinct * from {{ source('raw', 'subscription_months') }}

),

priced as (

    select
        account_id,
        cast(month_start as date) as month_start,
        plan,
        lower(trim(status)) as status_raw,
        coalesce(
            mrr,
            case plan
                when 'Starter' then 49
                when 'Growth' then 199
                when 'Scale' then 599
                when 'Enterprise' then 1999
            end
        ) as mrr_filled,
        mrr is null and plan is not null as mrr_was_filled
    from source

),

final as (

    select
        account_id,
        month_start,
        plan,
        case
            when status_raw = 'cancelled' then 'cancelled'
            when mrr_filled = 0 then 'cancelled'
            else 'active'
        end as status,
                case
            when status_raw = 'cancelled' then 0
            else mrr_filled
        end as mrr,
        mrr_was_filled
    from priced

)

select * from final