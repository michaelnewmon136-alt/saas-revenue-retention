with source as (

    select distinct * from {{ source('raw', 'product_usage') }}

),

cleaned as (

    select
        account_id,
        cast(month_start as date) as month_start,
        logins,
        active_users,
        logins is null as logins_missing
    from source

)

select * from cleaned