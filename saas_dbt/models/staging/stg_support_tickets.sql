with source as (

    select distinct * from {{ source('raw', 'support_tickets') }}

),

standardized as (

    select
        ticket_id,
        account_id,
        cast(created_date as date) as created_date,
        category,
        escalated,
        case
            when lower(trim(priority)) in ('high') then 'high'
            when lower(trim(priority)) in ('medium', 'med') then 'medium'
            when lower(trim(priority)) in ('low') then 'low'
            else null
        end as priority_clean
    from source

),

final as (

    select
        ticket_id,
        account_id,
        created_date,
        category,
        escalated,
        case
            when priority_clean is not null then priority_clean
            when escalated then 'high'
            else 'unknown'
        end as priority,
        priority_clean is null as priority_was_inferred
    from standardized

)

select * from final