-- Steal An Egg - Stealth Teleport & Safe Return Hu 🚀
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local CoreGui = game:GetService("CoreGui")
local LocalPlayer = Players.LocalPlayer

if CoreGui:FindFirstChild("EggHubGui") then
    CoreGui.EggHubGui:Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "EggHubGui"
pcall(function() ScreenGui.Parent = CoreGui end)
if not ScreenGui.Parent then ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui") end
ScreenGui.ResetOnSpawn = false

-- النافذة الرئيسية مرتبة وأكبر قليلاً لتستوعب القائمة
local MainFrame = Instance.new("Frame")
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
MainFrame.Position = UDim2.new(0.25, 0, 0.15, 0)
MainFrame.Size = UDim2.new(0, 280, 0, 380)
MainFrame.Active = true
MainFrame.Draggable = true

local Title = Instance.new("TextLabel")
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(10, 10, 15)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Text = "Stealth Teleport Hub 🚀"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 16
Title.Font = Enum.Font.SourceSansBold

-- دالة الانزلاق الخفي (Tween) لتنقل آمن بدون كشف أو رجوع
local function stealthTweenTo(targetCF)
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local root = char.HumanoidRootPart
        
        -- حساب المسافة لجعل سرعة الانزلاق ثابتة وسلسة
        local distance = (root.Position - targetCF.Position).Magnitude
        local speed = 350 -- كلما زاد الرقم زادت سرعة الانتقال الخفي
        local duration = math.clamp(distance / speed, 0.2, 1.5) -- تتراوح السرعة بين ثشر و ثانية ونصف حسب البعد
        
        -- إيقاف الفيزياء المؤقتة لمنع التضارب
        root.AssemblyLinearVelocity = Vector3.zero
        root.AssemblyAngularVelocity = Vector3.zero
        
        local tweenInfo = TweenInfo.new(duration, Enum.EasingStyle.Linear, Enum.EasingDirection.Out)
        local tween = TweenService:Create(root, tweenInfo, {CFrame = targetCF})
        
        tween:Play()
    end
end

-- زر العودة للبداية / القاعدة (بانزلاق خفي آمن)
local SpawnBtn = Instance.new("TextButton")
SpawnBtn.Parent = MainFrame
SpawnBtn.BackgroundColor3 = Color3.fromRGB(50, 120, 200)
SpawnBtn.Position = UDim2.new(0.1, 0, 0.15, 0)
SpawnBtn.Size = UDim2.new(0.8, 0, 0, 45)
SpawnBtn.Text = "العودة للبداية / القاعدة (خفي) 🛡️"
SpawnBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SpawnBtn.TextSize = 14
SpawnBtn.Font = Enum.Font.SourceSansBold

SpawnBtn.MouseButton1Click:Connect(function()
    stealthTweenTo(CFrame.new(0, 10, 0))
end)

-- قائمة العوالم والمراحل بترتيبها الحقيقي في الماب
local worldList = {
    "Forest (البداية)",
    "Lake",
    "Desert",
    "Jungle",
    "Snow",
    "Volcano",
    "Abyss Ocean",
    "Prehistoric",
    "Cosmic",
    "Cherry Blossom",
    "Titan Temple",
    "Demons",
    "Enchanted Forest (النهاية)"
}

local selectedWorld = worldList[1]

local DropdownBtn = Instance.new("TextButton")
DropdownBtn.Parent = MainFrame
DropdownBtn.BackgroundColor3 = Color3.fromRGB(35, 35, 45)
DropdownBtn.Position = UDim2.new(0.1, 0, 0.35, 0)
DropdownBtn.Size = UDim2.new(0.8, 0, 0, 38)
DropdownBtn.Text = "المرحلة: " .. selectedWorld .. " ▼"
DropdownBtn.TextColor3 = Color3.fromRGB(0, 255, 150)
DropdownBtn.TextSize = 13
DropdownBtn.Font = Enum.Font.SourceSansBold

local DropdownList = Instance.new("ScrollingFrame")
DropdownList.Parent = MainFrame
DropdownList.BackgroundColor3 = Color3.fromRGB(28, 28, 38)
DropdownList.Position = UDim2.new(0.1, 0, 0.46, 0)
DropdownList.Size = UDim2.new(0.8, 0, 0, 160)
DropdownList.Visible = false
DropdownList.CanvasSize = UDim2.new(0, 0, 3.5, 0)
DropdownList.ScrollBarThickness = 6

local UIListLayout = Instance.new("UIListLayout")
UIListLayout.Parent = DropdownList
UIListLayout.SortOrder = Enum.SortOrder.LayoutOrder

for _, wName in ipairs(worldList) do
    local opt = Instance.new("TextButton")
    opt.Parent = DropdownList
    opt.Size = UDim2.new(1, 0, 0, 30)
    opt.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
    opt.Text = wName
    opt.TextColor3 = Color3.fromRGB(255, 255, 255)
    opt.TextSize = 13
    opt.Font = Enum.Font.SourceSans
    
    opt.MouseButton1Click:Connect(function()
        selectedWorld = wName
        DropdownBtn.Text = "المرحلة: " .. wName .. " ▼"
        DropdownList.Visible = false
    end)
end

DropdownBtn.MouseButton1Click:Connect(function()
    DropdownList.Visible = not DropdownList.Visible
end)

-- زر الانتقال الخفي للمرحلة المحددة
local TeleportWorldBtn = Instance.new("TextButton")
TeleportWorldBtn.Parent = MainFrame
TeleportWorldBtn.BackgroundColor3 = Color3.fromRGB(80, 180, 80)
TeleportWorldBtn.Position = UDim2.new(0.1, 0, 0.78, 0)
TeleportWorldBtn.Size = UDim2.new(0.8, 0, 0, 45)
TeleportWorldBtn.Text = "الانتقال الخفي للمرحلة ⚡"
TeleportWorldBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
TeleportWorldBtn.TextSize = 14
TeleportWorldBtn.Font = Enum.Font.SourceSansBold

TeleportWorldBtn.MouseButton1Click:Connect(function()
    -- حساب مكان المرحلة بناءً على المسافة التقريبية لكل عالم (حوالي 350 بلوك للأمام لكل مرحلة)
    local index = 1
    for i, name in ipairs(worldList) do
        if name == selectedWorld then
            index = i - 1
            break
        end
    end
    
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local currentCF = char.HumanoidRootPart.CFrame
        -- الانتقال للأمام بمسافة محسوبة بدقة لكل عالم لتستقر أمام البيض والوحوش مباشرة
        local targetCF = currentCF + Vector3.new(0, 0, -(index * 320))
        
        stealthTweenTo(targetCF)
    end
end)
