-- Steal An Egg - Fixed Auto Steal Hub
local Players = game:GetService("Players")
local LocalPlayer = Players.LocalPlayer
local PlayerGui = LocalPlayer:WaitForChild("PlayerGui")

if PlayerGui:FindFirstChild("EggHubGui") then
    PlayerGui.EggHubGui:Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "EggHubGui"
ScreenGui.Parent = PlayerGui
ScreenGui.ResetOnSpawn = false

-- النافذة الرئيسية
local MainFrame = Instance.new("Frame")
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
MainFrame.Position = UDim2.new(0.3, 0, 0.2, 0)
MainFrame.Size = UDim2.new(0, 260, 0, 360)
MainFrame.Active = true
MainFrame.Draggable = true

-- عنوان القائمة
local Title = Instance.new("TextLabel")
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(10, 10, 15)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Text = "Steal An Egg - Target Hub 🚀"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 16
Title.Font = Enum.Font.SourceSansBold

-- عنوان الاختيار
local TargetLabel = Instance.new("TextLabel")
TargetLabel.Parent = MainFrame
TargetLabel.BackgroundTransparency = 1
TargetLabel.Position = UDim2.new(0.1, 0, 0.13, 0)
TargetLabel.Size = UDim2.new(0.8, 0, 0, 20)
TargetLabel.Text = "اختر نوع البيضة المستهدفة:"
TargetLabel.TextColor3 = Color3.fromRGB(180, 180, 180)
TargetLabel.TextSize = 13
TargetLabel.Font = Enum.Font.SourceSans

-- زر القائمة المنسدلة (Dropdown)
local DropdownBtn = Instance.new("TextButton")
DropdownBtn.Parent = MainFrame
DropdownBtn.BackgroundColor3 = Color3.fromRGB(35, 35, 45)
DropdownBtn.Position = UDim2.new(0.1, 0, 0.20, 0)
DropdownBtn.Size = UDim2.new(0.8, 0, 0, 35)
DropdownBtn.Text = "Any Egg (أي بيضة) ▼"
DropdownBtn.TextColor3 = Color3.fromRGB(0, 255, 150)
DropdownBtn.TextSize = 14
DropdownBtn.Font = Enum.Font.SourceSansBold

-- إطار خيارات القائمة المنسدلة
local DropdownList = Instance.new("ScrollingFrame")
DropdownList.Parent = MainFrame
DropdownList.BackgroundColor3 = Color3.fromRGB(28, 28, 38)
DropdownList.Position = UDim2.new(0.1, 0, 0.31, 0)
DropdownList.Size = UDim2.new(0.8, 0, 0, 110)
DropdownList.Visible = false
DropdownList.CanvasSize = UDim2.new(0, 0, 2, 0)
DropdownList.ScrollBarThickness = 5

local UIListLayout = Instance.new("UIListLayout")
UIListLayout.Parent = DropdownList
UIListLayout.SortOrder = Enum.SortOrder.LayoutOrder

local presetTargets = {"Any Egg (أي بيضة)", "Secret", "Divine", "Mythical"}

-- زر التحديث
local RefreshBtn = Instance.new("TextButton")
RefreshBtn.Parent = MainFrame
RefreshBtn.BackgroundColor3 = Color3.fromRGB(45, 45, 60)
RefreshBtn.Position = UDim2.new(0.1, 0, 0.65, 0)
RefreshBtn.Size = UDim2.new(0.8, 0, 0, 32)
RefreshBtn.Text = "تحديث فحص الخريطة 🔄"
RefreshBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
RefreshBtn.TextSize = 13
RefreshBtn.Font = Enum.Font.SourceSansBold

-- زر السرقة التلقائية
local AutoStealBtn = Instance.new("TextButton")
AutoStealBtn.Parent = MainFrame
AutoStealBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
AutoStealBtn.Position = UDim2.new(0.1, 0, 0.76, 0)
AutoStealBtn.Size = UDim2.new(0.8, 0, 0, 38)
AutoStealBtn.Text = "Auto Steal: [OFF]"
AutoStealBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
AutoStealBtn.TextSize = 15
AutoStealBtn.Font = Enum.Font.SourceSansBold

-- زر منطقة الأمان
local SafeZoneBtn = Instance.new("TextButton")
SafeZoneBtn.Parent = MainFrame
SafeZoneBtn.BackgroundColor3 = Color3.fromRGB(50, 120, 200)
SafeZoneBtn.Position = UDim2.new(0.1, 0, 0.88, 0)
SafeZoneBtn.Size = UDim2.new(0.8, 0, 0, 32)
SafeZoneBtn.Text = "العودة لمنطقة الأمان 🛡️"
SafeZoneBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SafeZoneBtn.TextSize = 13
SafeZoneBtn.Font = Enum.Font.SourceSansBold

-- ==========================================
-- منطق القائمة والبحث المطور في مجلدات الماب
-- ==========================================

local selectedTargetName = "Any Egg (أي بيضة)"
local autoStealActive = false

local function setupDropdown()
    for _, child in ipairs(DropdownList:GetChildren()) do
        if child:IsA("TextButton") then child:Destroy() end
    end
    
    for _, target in ipairs(presetTargets) do
        local OptionBtn = Instance.new("TextButton")
        OptionBtn.Parent = DropdownList
        OptionBtn.Size = UDim2.new(1, 0, 0, 25)
        OptionBtn.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
        OptionBtn.Text = target
        OptionBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
        OptionBtn.TextSize = 12
        OptionBtn.Font = Enum.Font.SourceSans
        
        OptionBtn.MouseButton1Click:Connect(function()
            selectedTargetName = target
            DropdownBtn.Text = target .. " ▼"
            DropdownList.Visible = false
        end)
    end
end

DropdownBtn.MouseButton1Click:Connect(function()
    DropdownList.Visible = not DropdownList.Visible
end)

-- وظيفة فحص دقيقة تبحث في كافة المجلدات بالخريطة عن البيض
local function findEggInMap()
    local targetKey = selectedTargetName:lower()
    if targetKey:find("any") then targetKey = "egg" end

    -- فحص العناصر داخل Workspace ومجلداتها الفرعية (مثل Drops أو Eggs)
    for _, obj in ipairs(workspace:GetDescendants()) do
        local nameLower = obj.Name:lower()
        
        -- التحقق مما إذا كان العنصر عبارة عن بيضة أو عش أو يحتوي على الكلمة المستهدفة
        if nameLower:find(targetKey) or nameLower:find("egg") or nameLower:find("nest") then
            -- استبعاد اللاعبين والأدوات الشخصية
            if not obj:IsDescendantOf(Players) then
                if obj:IsA("Model") and obj.PrimaryPart then
                    return obj.PrimaryPart
                elseif obj:IsA("BasePart") and not obj.Anchored and obj.Size.Magnitude < 15 then
                    return obj
                elseif obj:IsA("BasePart") then
                    return obj
                end
            end
        end
    end
    return nil
end

AutoStealBtn.MouseButton1Click:Connect(function()
    autoStealActive = not autoStealActive
    
    if autoStealActive then
        AutoStealBtn.Text = "Auto Steal: [ON]"
        AutoStealBtn.BackgroundColor3 = Color3.fromRGB(50, 200, 80)
        
        task.spawn(function()
            while autoStealActive do
                local char = LocalPlayer.Character
                if char and char:FindFirstChild("HumanoidRootPart") then
                    local eggPart = findEggInMap()
                    if eggPart then
                        -- الانتقال المباشر للبيضة
                        char.HumanoidRootPart.CFrame = eggPart.CFrame + Vector3.new(0, 3, 0)
                    end
                end
                task.wait(0.8) -- فحص سريع جداً كل 0.8 ثانية لضمان سرقة البيضة قبل البقية
            end
        end)
    else
        AutoStealBtn.Text = "Auto Steal: [OFF]"
        AutoStealBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
    end
end)

RefreshBtn.MouseButton1Click:Connect(function()
    RefreshBtn.Text = "تم التحديث! ✅"
    task.wait(1)
    RefreshBtn.Text = "تحديث فحص الخريطة 🔄"
end)

SafeZoneBtn.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local spawn = workspace:FindFirstChild("SpawnLocation") or workspace:FindFirstChild("Spawn")
        if spawn then
            char.HumanoidRootPart.CFrame = spawn.CFrame + Vector3.new(0, 3, 0)
        else
            char.HumanoidRootPart.CFrame = CFrame.new(0, 10, 0)
        end
    end
end)

setupDropdown()
