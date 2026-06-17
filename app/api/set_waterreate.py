from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db_connection
from app.core.jwt import get_current_user
from app.schemas.basemodel_ratewater import WaterRateVersionCreate
import pymysql.cursors

router = APIRouter()


# แสดงอัตราค่าน้ำปัจจุบัน
@router.get("/water-rates")
async def get_water_rates(
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT
                    wr.rate_id,
                    wr.min_unit,
                    wr.max_unit,
                    wr.price_per_unit,
                    wr.effective_from,
                    wr.is_active,
                    e.full_name AS created_by_name
                FROM water_rates wr
                LEFT JOIN employees e
                    ON wr.created_by = e.emp_id
                WHERE wr.is_active = 1
                ORDER BY wr.min_unit ASC
            """)

            rates = cursor.fetchall()

            return {
                "success": True,
                "count": len(rates),
                "data": rates
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        conn.close()


# สร้างชุดอัตราค่าน้ำใหม่
@router.post("/water-rates", status_code=201)
async def create_water_rate_version(
    water_rate: WaterRateVersionCreate,
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:

            # ตรวจสอบ min/max
            for rate in water_rate.rates:
                if rate.min_unit > rate.max_unit:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid range {rate.min_unit}-{rate.max_unit}"
                    )

            # ตรวจสอบช่วงซ้อนกัน
            sorted_rates = sorted(
                water_rate.rates,
                key=lambda x: x.min_unit
            )

            for i in range(len(sorted_rates) - 1):
                current_rate = sorted_rates[i]
                next_rate = sorted_rates[i + 1]

                if current_rate.max_unit >= next_rate.min_unit:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Rate ranges overlap: "
                            f"{current_rate.min_unit}-{current_rate.max_unit} "
                            f"and "
                            f"{next_rate.min_unit}-{next_rate.max_unit}"
                        )
                    )

            # ปิดชุดเดิมทั้งหมด
            cursor.execute("""
                UPDATE water_rates
                SET is_active = 0
                WHERE is_active = 1
            """)

            # เพิ่มชุดใหม่
            for rate in sorted_rates:
                cursor.execute(
                    """
                    INSERT INTO water_rates
                    (
                        min_unit,
                        max_unit,
                        price_per_unit,
                        effective_from,
                        is_active,
                        created_at,
                        created_by
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        1,
                        NOW(),
                        %s
                    )
                    """,
                    (
                        rate.min_unit,
                        rate.max_unit,
                        rate.price_per_unit,
                        water_rate.effective_from,
                        current_user["emp_id"]  # ใช้ emp_id จาก JWT
                    )
                )

            conn.commit()

            return {
                "success": True,
                "message": "Water rate version created successfully",
                "effective_from": str(water_rate.effective_from),
                "total_rates": len(sorted_rates)
            }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        conn.close()